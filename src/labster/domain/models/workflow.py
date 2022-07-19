"""Modèle de case management adapté au projet Labster."""
from __future__ import annotations

from collections.abc import Container
from datetime import date, datetime
from typing import Dict

import structlog

from labster.domain.services.notifications import send_email
from labster.forms.workflow import ConfirmerFinalisationForm, \
    ConfirmerRecevabiliteForm, WorkflowForm
from labster.lib.workflow import State, Transition, Workflow

logger = structlog.get_logger()


class EnEdition(State):
    label = "En édition"
    next_action = "Edition à finaliser et à soumettre"

    def on_enter(self, workflow):
        case = workflow.case
        case.active = True
        case.editable = True

    def task_owners(self, workflow):
        case = workflow.case
        return {u for u in [case.gestionnaire, case.porteur] if u}


class EnValidation(State):
    label = "En cours de validation hiérarchique"
    label_short = "En validation"
    next_action = "Demande à considérer pour validation"

    def task_owners(self, workflow):
        demande = workflow.case
        # assert validation_stage
        if not demande.wf_stage:
            logger.warning(
                f"Warning: la demande {demande.id} n'a pas de validation_stage"
            )
            demande.wf_stage = next_validation_stage(demande)
        return demande.wf_stage.direction


def next_validation_stage(demande):
    from labster.domain.models.unites import DEPARTEMENT, EQUIPE, LABORATOIRE

    structure = demande.structure
    stage = demande.wf_stage

    if not stage:
        stage = structure
        if stage.type == EQUIPE and not structure.wf_must_validate(EQUIPE):
            stage = stage.parent
        if stage.type == DEPARTEMENT and not structure.wf_must_validate(DEPARTEMENT):
            stage = stage.parent
        if stage.type == LABORATOIRE and not structure.wf_must_validate(LABORATOIRE):
            stage = None
        assert stage is None or stage.type in [EQUIPE, DEPARTEMENT, LABORATOIRE]
        return stage

    stage = stage.parent
    if not stage:
        return None

    if stage.type == DEPARTEMENT and not structure.wf_must_validate(DEPARTEMENT):
        stage = stage.parent
    if not stage:
        return None

    if stage.type == LABORATOIRE and not structure.wf_must_validate(LABORATOIRE):
        stage = None
    if not stage:
        return None

    if stage == None or stage.type in [DEPARTEMENT, LABORATOIRE]:
        return stage

    return None


class EnVerification(State):
    label = "Recevabilité en cours de vérification"
    label_short = "En vérification"
    next_action = "Recevabilité à confirmer"

    def on_enter(self, workflow):
        workflow.set_value("ar_envoye", False)

    def task_owners(self, workflow):
        case = workflow.case
        if case.contact_dgrtt:
            return [case.contact_dgrtt]
        else:
            return []


class EnInstruction(State):
    label = "En cours d'instruction par la DR&I"
    label_short = "En instruction"
    next_action = "Instruction à mener et finaliser"

    def task_owners(self, workflow):
        case = workflow.case
        if case.contact_dgrtt:
            return [case.contact_dgrtt]
        else:
            return []


# Etats finaux
class Traitee(State):
    label = "Traitée par la DR&I"
    label_short = "Traitée"
    is_final = True


class Rejetee(State):
    label = "Rejetée par la DR&I"
    label_short = "Rejetée"
    is_final = True


class Abandonnee(State):
    label = "Abandonnée par le porteur"
    label_short = "Abandonnée"
    is_final = True


EN_EDITION = EnEdition()
EN_VALIDATION = EnValidation()
EN_VERIFICATION = EnVerification()
EN_INSTRUCTION = EnInstruction()
TRAITEE = Traitee()
REJETEE = Rejetee()
ABANDONNEE = Abandonnee()

ACTIVE_STATES: list[State] = [
    EN_EDITION,
    EN_VALIDATION,
    EN_VERIFICATION,
    EN_INSTRUCTION,
]
INACTIVE_STATES: list[State] = [TRAITEE, REJETEE, ABANDONNEE]
ALL_STATES: list[State] = ACTIVE_STATES + INACTIVE_STATES


#
# Transitions
#
class Abandonner(Transition):
    label = "Abandonner la demande"
    category = "danger"
    from_states = [EN_EDITION, EN_VALIDATION, EN_VERIFICATION, EN_INSTRUCTION]
    to_state = ABANDONNEE
    message = "{actor} a abandonné la demande."

    def precondition(self, workflow):
        return workflow.actor_is_porteur_or_gdl()

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        if old_state == EN_EDITION:
            return []
        if old_state == EN_VALIDATION:
            return case.owners + case.structure.direction
        if old_state in (EN_VERIFICATION, EN_INSTRUCTION):
            return case.owners + [case.contact_dgrtt]
        raise RuntimeError(f"Unknown state: {old_state}")


class Desarchiver(Transition):
    label = "Désarchiver la demande"
    category = "danger"
    from_states = [ABANDONNEE, REJETEE, TRAITEE]
    message = "{actor} a désarchivé la demande."

    def apply(self, workflow, data):
        from labster.domain.models.demandes import Demande

        demande = workflow.case  # type: Demande
        old_state_id = demande.wf_history[-1].get("old_state", "EN_EDITION")
        old_state = workflow.get_state_by_id(old_state_id)
        old_state.enter(workflow)
        demande.active = True
        demande.editable = True

    def get_form(self, workflow, **kw):
        return WorkflowForm(require_note=True)

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners


class Soumettre(Transition):
    label = "Soumettre la demande"
    from_states = [EN_EDITION]

    def precondition(self, workflow):
        demande = workflow.case
        structure = demande.structure

        if not demande.is_valid():
            return False

        if workflow.actor == demande.porteur:
            return True

        # Cas à gérer: la demande est issue d'une sous-structure dans
        # le périmètre du gestionnaire.
        #
        # demande.structure et workflow.actor.structure peuvent être différentes.
        #
        # Par exemple:
        # demande.structure = equipe Developpement des circuits neuronaux
        # workflow.actor.structure = Institut de la vision
        # Et dans ce cas
        # demande.structure.get_gestionnaires() = []
        #
        # Sur le formulaire de la demande, l'utilisateur voit
        # "Institut de la vision", donc peut aller changer son paramètre "permettre_soummission_directe" à True
        # On a donc
        # demande.structure.permettre_soummission_directe inchangé, potentiellement à False,
        # et workflow.actor.structure.permettre_soummission_directe à True.
        #
        # On a donc besoin des deux "if" suivants.
        if (
            workflow.actor.structure
            and workflow.actor.structure.permettre_soummission_directe
            and workflow.actor in workflow.actor.structure.get_gestionnaires()
        ):
            return True

        if (
            structure.permettre_soummission_directe
            and workflow.actor in structure.get_gestionnaires()
        ):
            return True

        if (
            workflow.get_value("validee_hierarchie")
            and structure.permettre_reponse_directe
            and workflow.actor == demande.gestionnaire
        ):
            return True

        return False

    def apply(self, workflow, data):
        demande = workflow.case
        demande.editable = False

        if data.get("resoumission"):
            workflow.set_value("validee_hierarchie", False)

        if workflow.get_value("validee_hierarchie"):
            if workflow.get_value("recevable"):
                EN_INSTRUCTION.enter(workflow)
            else:
                EN_VERIFICATION.enter(workflow)
        else:
            demande.wf_stage = next_validation_stage(demande)
            EN_VALIDATION.enter(workflow)

    def message(self, workflow):
        if workflow.get_value("validee_hierarchie"):
            return "{actor} a resoumis sa demande sans revalidation hiérarchique"
        else:
            return "{actor} a soumis sa demande pour validation hiérarchique."

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        if workflow.get_value("validee_hierarchie"):
            return [case.contact_dgrtt]
        else:
            return case.wf_stage.direction

    def get_form(self, workflow, **kw):
        if workflow.get_value("validee_hierarchie"):
            return WorkflowForm(ask_for_revalidation=True)

        return WorkflowForm()


#
# Prendre la main
#
class AbstractPrendreLaMain(Transition):
    label = "Prendre la main sur la demande"
    category = "danger"
    message = "{actor} a pris la main sur la demande."

    def get_users_to_notify(self, workflow, old_state):
        from labster.domain.models.profiles import Profile

        case = workflow.case
        actor = workflow.actor
        user_ids = {entry["actor_id"] for entry in case.wf_history}
        users = []
        for id in user_ids:
            try:
                user = Profile.query.get(id)
                if user != actor:
                    users.append(user)
            except Exception:
                pass
        return users


class PrendreLaMainGestionnaire(AbstractPrendreLaMain):
    from_states = ACTIVE_STATES

    def precondition(self, workflow):
        case = workflow.case
        actor = workflow.actor
        return actor.has_role("gestionnaire", case) and actor not in (
            case.gestionnaire,
            case.porteur,
        )

    def apply(self, workflow, data):
        case = workflow.case
        actor = workflow.actor
        case.gestionnaire = actor


class PrendreLaMainDgrtt(AbstractPrendreLaMain):
    from_states = ACTIVE_STATES

    def precondition(self, workflow):
        case = workflow.case
        actor = workflow.actor
        return actor.has_role("dgrtt") and not actor == case.contact_dgrtt

    def apply(self, workflow, data):
        case = workflow.case
        actor = workflow.actor
        case.contact_dgrtt = actor


#
# "Valider demande (hiérarchie)
#
class ValiderDir(Transition):
    label = "Valider la demande"
    from_states = [EN_VALIDATION]
    message = "Demande validée par la hiérarchie ({actor})."

    def precondition(self, workflow):
        return workflow.actor in workflow.state.task_owners(workflow)

    def apply(self, workflow, data):
        demande = workflow.case
        demande.assigne_contact_dgrtt()
        workflow.set_value("validee_hierarchie", True)
        demande.date_effective = date.today()

        next_stage = next_validation_stage(demande)
        demande.wf_stage = next_stage
        if not next_stage:
            EN_VERIFICATION.enter(workflow)

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        if case.contact_dgrtt:
            return case.owners + [case.contact_dgrtt]
        else:
            return case.owners


class RequerirModificationDir(Transition):
    label = "Requérir modification / complément"
    from_states = [EN_VALIDATION]
    to_state = EN_EDITION
    message = (
        "Demande de compléments / modifications par {actor} "
        "(direction labo/département/équipe) pour vérification de recevabilité."
    )

    def precondition(self, workflow):
        return workflow.actor in workflow.state.task_owners(workflow)

    def apply(self, workflow, data):
        demande = workflow.case
        demande.wf_stage = None
        workflow.set_value("validee_hierarchie", False)

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners

    def get_form(self, workflow, **kw):
        return WorkflowForm(require_note=True)


#
# DGRTT (renommé DR&I)
#
class AccuserReception(Transition):
    label = "Accuser réception en attendant vérification ultérieure"
    from_states = [EN_VERIFICATION]
    to_state = EN_VERIFICATION
    message = "Accusé de réception envoyé par {actor} (contact)."

    def precondition(self, workflow):
        return workflow.actor_is_contact_dgrtt() and not workflow.get_value(
            "ar_envoye", False
        )

    def apply(self, workflow, data):
        workflow.set_value("ar_envoye", True)

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners


class RequerirModificationDgrtt(Transition):
    label = "Requérir modification / complément"
    from_states = [EN_VERIFICATION, EN_INSTRUCTION]
    to_state = EN_EDITION

    def precondition(self, workflow):
        return workflow.actor_is_contact_dgrtt()

    def apply(self, workflow, data):
        if data.get("resoumission"):
            workflow.set_value("validee_hierarchie", False)

    def message(self, workflow):
        if workflow.state == EN_VERIFICATION:
            return (
                "Demande de compléments / modifications par {actor} "
                "(contact) pour vérification de recevabilité."
            )
        else:
            return (
                "Demande de compléments / modifications par {actor} "
                "(contact) pour instruction."
            )

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners

    def get_form(self, workflow, **kw):
        if workflow.get_value("validee_hierarchie"):
            return WorkflowForm(ask_for_revalidation=True, require_note=True)

        return WorkflowForm(require_note=True)


class ConfirmerRecevabiliteDgrtt(Transition):
    label = "Confirmer recevabilité"
    from_states = [EN_VERIFICATION]
    to_state = EN_INSTRUCTION

    def precondition(self, workflow):
        return workflow.actor_is_contact_dgrtt()

    def apply(self, workflow, data):
        workflow.set_value("recevable", True)
        self.send_notification(workflow)

    def send_notification(self, workflow):
        case = workflow.case
        subject = "Recevabilité de votre demande par la DR&I"
        ctx = {
            "transition": self,
            "demande": case,
            "workflow": workflow,
            "now": datetime.now(),
        }
        send_email(case.owners, subject, "notif-demande-recevable.html", ctx)

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners

    def get_form(self, workflow, **kw):
        return ConfirmerRecevabiliteForm()

    def message(self, workflow):
        demande = workflow.case
        tpl = (
            "Recevabilité confirmée par {actor} (contact). "
            "No Infolab: %s." % demande.no_infolab
        )
        return tpl


class ConfirmerFinalisationDgrtt(Transition):
    label = "Confirmer finalisation"
    from_states = [EN_INSTRUCTION]
    to_state = TRAITEE

    def precondition(self, workflow):
        return workflow.actor_is_contact_dgrtt()

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners

    def get_form(self, workflow, **kw):
        return ConfirmerFinalisationForm()

    def apply(self, workflow, data):
        self.send_notification(workflow)

    def send_notification(self, workflow):
        case = workflow.case
        ctx = {
            "transition": self,
            "demande": case,
            "workflow": workflow,
            "now": datetime.now(),
        }
        subject = "Finalisation de votre demande par la DR&I"
        du = case.laboratoire.direction
        recipients = case.owners + du
        send_email(recipients, subject, "notif-demande-finalisee.html", ctx)

    def message(self, workflow):
        demande = workflow.case
        tpl = (
            "Traitement finalisé par {actor} (contact)."
            "No eOTP: %s." % demande.no_eotp
        )
        return tpl


class RejeterDgrtt(Transition):
    label = "Rejeter / abandonner demande"
    category = "danger"
    from_states = [EN_EDITION, EN_VALIDATION, EN_VERIFICATION, EN_INSTRUCTION]
    to_state = REJETEE
    message = "Demande rejetée / abandonnées par {actor} (contact)."

    def precondition(self, workflow):
        actor = workflow.actor
        return actor.has_role("dgrtt")

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners

    def apply(self, workflow, data):
        # type: (Workflow, Dict) -> None
        self.send_notification(workflow)

    def send_notification(self, workflow):
        # type: (Workflow) -> None
        case = workflow.case
        ctx = {
            "transition": self,
            "demande": case,
            "workflow": workflow,
            "now": datetime.now(),
        }
        subject = "Rejet de votre demande par la DR&I"
        send_email(case.owners, subject, "notif-demande-rejetee.html", ctx)

    def get_form(self, workflow, **kw):
        return WorkflowForm(require_note=True)


class Commenter(Transition):
    label = "Envoyer un message"
    category = "success"
    from_states = [EN_EDITION, EN_VERIFICATION, EN_INSTRUCTION]
    message = "{actor} a posté le commentaire ou la question suivante: "

    def precondition(self, workflow):
        # type: (Workflow) -> bool

        actor = workflow.actor
        demande = workflow.case
        if workflow.state == EN_EDITION and not demande.contact_dgrtt:
            return False
        return actor in self._get_stakeholder(workflow)

    def get_users_to_notify(self, workflow, old_state):
        return self._get_stakeholder(workflow)

    def _get_stakeholder(self, workflow):
        # type: (Workflow) -> Container
        from .profiles import Profile
        from .unites import OrgUnit

        demande = workflow.case
        structure = demande.structure  # type: OrgUnit

        stakeholders = set(demande.owners)
        if demande.contact_dgrtt:
            stakeholders.add(demande.contact_dgrtt)

        directeurs = structure.get_directeurs()
        for directeur in directeurs:
            stakeholders.add(directeur)

        for history_item in demande.wf_history:
            actor_id = history_item["actor_id"]
            if actor_id:
                actor = Profile.query.get(actor_id)
                stakeholders.add(actor)

        return stakeholders

    def get_form(self, workflow, **kw):
        return WorkflowForm(require_note=True)

    def apply(self, workflow, data):
        # type: (Workflow, Dict) -> None
        self.send_notification(workflow)

    def send_notification(self, workflow):
        # type: (Workflow) -> None
        case = workflow.case
        ctx = {
            "transition": self,
            "demande": case,
            "workflow": workflow,
            "now": datetime.now(),
        }
        subject = "Un commentaire sur votre demande"
        send_email(case.owners, subject, "notif-demande-comment.html", ctx)


#
ABANDONNER = Abandonner()
DESARCHIVER = Desarchiver()
SOUMETTRE = Soumettre()
PRENDRE_LA_MAIN_GESTIONNAIRE = PrendreLaMainGestionnaire()
PRENDRE_LA_MAIN_DGRTT = PrendreLaMainDgrtt()
#
VALIDER_DIR = ValiderDir()
REQUERIR_MODIFICATION_DIR = RequerirModificationDir()
#
ACCUSER_RECEPTION = AccuserReception()
REQUERIR_MODIFICATION_DGRTT = RequerirModificationDgrtt()
CONFIRMER_RECEVABILITE_DGRTT = ConfirmerRecevabiliteDgrtt()
CONFIRMER_FINALISATION_DGRTT = ConfirmerFinalisationDgrtt()
REJETER_DGRTT = RejeterDgrtt()
#
COMMENTER = Commenter()


#
# Workflow
#
class LabsterWorkflow(Workflow):
    initial_state = EN_EDITION

    states = ALL_STATES

    # NB: order counts!
    transitions = [
        SOUMETTRE,
        PRENDRE_LA_MAIN_GESTIONNAIRE,
        VALIDER_DIR,
        PRENDRE_LA_MAIN_DGRTT,
        REQUERIR_MODIFICATION_DIR,
        ACCUSER_RECEPTION,
        CONFIRMER_RECEVABILITE_DGRTT,
        CONFIRMER_FINALISATION_DGRTT,
        REQUERIR_MODIFICATION_DGRTT,
        REJETER_DGRTT,
        ABANDONNER,
        DESARCHIVER,
        COMMENTER,
    ]

    def actor_is_contact_dgrtt(self):
        return self.actor == self.case.contact_dgrtt

    def actor_is_porteur_or_gdl(self):
        return self.actor in (self.case.porteur, self.case.gestionnaire)
