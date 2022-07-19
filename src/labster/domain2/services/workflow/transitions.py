"""Modèle de case management adapté au projet Labster."""
from __future__ import annotations

from collections.abc import Container
from datetime import date, datetime
from typing import TYPE_CHECKING

import structlog

from labster.domain2.services.notifications import send_email
from labster.domain2.services.roles import Role
from labster.lib.workflow import Transition, Workflow

from .forms import get_form
from .states import ABANDONNEE, ACTIVE_STATES, EN_EDITION, EN_INSTRUCTION, \
    EN_VALIDATION, EN_VERIFICATION, REJETEE, TRAITEE

if TYPE_CHECKING:
    from labster.domain2.model.demande import Demande
    from labster.domain2.model.profile import Profile

logger = structlog.get_logger()


#
# Transitions
#
class BaseTransition(Transition):
    def get_form(self, workflow, **kw):
        return get_form()


class Abandonner(BaseTransition):
    label = "Abandonner la demande"
    category = "danger"
    from_states = [EN_EDITION, EN_VALIDATION, EN_VERIFICATION, EN_INSTRUCTION]
    to_state = ABANDONNEE
    message = "{actor} a abandonné la demande."

    def precondition(self, workflow: Workflow):
        return workflow.actor_is_porteur_or_gestionnaire()

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case

        if old_state == EN_EDITION:
            return set()

        if old_state == EN_VALIDATION:
            # FIXME
            # return case.owners + case.structure.direction
            return case.owners

        if old_state in (EN_VERIFICATION, EN_INSTRUCTION):
            return case.owners | {case.contact_labco}

        raise RuntimeError(f"Unknown state: {old_state}")


class Desarchiver(BaseTransition):
    label = "Désarchiver la demande"
    category = "danger"
    from_states = [ABANDONNEE, REJETEE, TRAITEE]
    message = "{actor} a désarchivé la demande."

    def apply(self, workflow, data):
        demande: Demande = workflow.case
        old_state_id = demande.wf_history[-1].get("old_state", "EN_EDITION")
        old_state = workflow.get_state_by_id(old_state_id)
        old_state.enter(workflow)
        demande.active = True
        demande.editable = True

    def get_form(self, workflow, **kw):
        return get_form(require_note=True)

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners


class Soumettre(BaseTransition):
    label = "Soumettre la demande"
    from_states = [EN_EDITION]

    def precondition(self, workflow):
        demande = workflow.case
        structure_de_la_demande = demande.structure
        actor = workflow.actor

        if not demande.is_valid():
            return False

        # Le porteur peut toujours soumettre
        if actor == demande.porteur:
            return True

        if (
            actor.has_role(Role.GESTIONNAIRE, structure_de_la_demande)
            and structure_de_la_demande.permettre_soummission_directe
        ):
            return True

        if actor == demande.gestionnaire and workflow.get_value("validee_hierarchie"):
            return True

        return False

        #
        # TODO: vérifier si c'est OK.
        #
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
        # "Institut de la vision", donc peut aller changer son paramètre
        # "permettre_soummission_directe" à True
        # On a donc
        # demande.structure.permettre_soummission_directe inchangé, potentiellement à False,
        # et workflow.actor.structure.permettre_soummission_directe à True.
        #
        # On a donc besoin des deux "if" suivants.

        # if structure_de_l_acteur.permettre_soummission_directe:
        #     if (
        #         actor in structure_de_l_acteur.get_gestionnaires()
        #     ):
        #         return True
        #
        #     if (
        #         actor in structure_de_la_demande.get_gestionnaires()
        #     ):
        #         return True
        #
        #     if (
        #         workflow.get_value("validee_hierarchie")
        #         and actor == demande.gestionnaire
        #     ):
        #         return True
        #
        # return False

    def apply(self, workflow, data):
        demande = workflow.case
        demande.editable = False

        if data.get("resoumission"):
            workflow.set_value("validee_hierarchie", False)
            workflow.set_value("signatures", [])

        if workflow.get_value("validee_hierarchie"):
            if workflow.get_value("recevable"):
                EN_INSTRUCTION.enter(workflow)
            else:
                EN_VERIFICATION.enter(workflow)
        else:
            EN_VALIDATION.enter(workflow)

    def message(self, workflow):
        if workflow.get_value("validee_hierarchie"):
            return "{actor} a resoumis sa demande sans revalidation hiérarchique"
        else:
            return "{actor} a soumis sa demande pour validation hiérarchique."

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case

        if workflow.get_value("validee_hierarchie"):
            return {case.contact_labco}

        structure = case.structure
        result = structure.responsables
        for structure_concernee in case.get_structure_concernees():
            result |= structure_concernee.responsables

        return result

    def get_form(self, workflow, **kw):
        ask_for_revalidation = workflow.get_value("validee_hierarchie")
        return get_form(ask_for_revalidation=ask_for_revalidation)


#
# Prendre la main
#
class AbstractPrendreLaMain(BaseTransition):
    label = "Prendre la main sur la demande"
    category = "danger"
    message = "{actor} a pris la main sur la demande."

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        actor = workflow.actor
        user_ids = {entry["actor_id"] for entry in case.wf_history}
        users = set()
        for id in user_ids:
            try:
                # TODO
                user = Profile.query.get(id)
                if user != actor:
                    users.add(user)
            except Exception:
                pass
        return users


class PrendreLaMainGestionnaire(AbstractPrendreLaMain):
    from_states = ACTIVE_STATES

    def precondition(self, workflow: Workflow):
        from labster.rbac import is_gestionnaire

        case = workflow.case
        actor = workflow.actor

        return is_gestionnaire(actor, case) and actor not in (
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
        from labster.rbac import is_membre_drv

        case = workflow.case
        actor = workflow.actor

        if actor == case.contact_labco:
            return False

        if actor.is_membre_dri():
            return True

        if is_membre_drv(actor, case.structure):
            return True

        return False

    def apply(self, workflow, data):
        case = workflow.case
        actor = workflow.actor
        case.contact_labco = actor


#
# "Valider demande
#
class ValiderDir(BaseTransition):
    label = "Valider la demande"
    from_states = [EN_VALIDATION]
    message = "Demande validée par un responsable ({actor})."

    def precondition(self, workflow):
        return workflow.actor in workflow.state.task_owners(workflow)

    def apply(self, workflow, data):
        demande = workflow.case
        actor = workflow.actor

        signatures: set[str] = set(workflow.get_value("signatures") or [])

        structures_signataires = demande.structures_signataires()
        for structure in structures_signataires:
            if actor.has_role(Role.RESPONSABLE, structure):
                signatures.add(structure.id)

        workflow.set_value("signatures", list(signatures))

        structures_signataires_restantes = {
            s for s in structures_signataires if s.id not in signatures
        }

        if not structures_signataires_restantes:
            demande.assigne_contact_labco()
            workflow.set_value("validee_hierarchie", True)
            demande.date_effective = date.today()
            EN_VERIFICATION.enter(workflow)
            return

    def get_users_to_notify(self, workflow, old_state) -> set[Profile]:
        case = workflow.case
        if case.contact_labco:
            return case.owners | {case.contact_labco}
        else:
            return case.owners


class RequerirModificationDir(BaseTransition):
    label = "Requérir modification / complément"
    from_states = [EN_VALIDATION]
    to_state = EN_EDITION
    message = (
        "Demande de compléments / modifications par {actor} "
        "(responsable labo/département/équipe) pour vérification de recevabilité."
    )

    def precondition(self, workflow):
        return workflow.actor in workflow.state.task_owners(workflow)

    def apply(self, workflow, data):
        workflow.set_value("validee_hierarchie", False)
        workflow.set_value("signatures", [])

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners

    def get_form(self, workflow, **kw):
        return get_form(require_note=True)


#
# DGRTT (renommé DR&I)
#
class AccuserReception(BaseTransition):
    label = "Accuser réception en attendant vérification ultérieure"
    from_states = [EN_VERIFICATION]
    to_state = EN_VERIFICATION
    message = "Accusé de réception envoyé par {actor} (contact)."

    def precondition(self, workflow):
        return workflow.actor_is_contact_labco() and not workflow.get_value(
            "ar_envoye", False
        )

    def apply(self, workflow, data):
        workflow.set_value("ar_envoye", True)

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners


class RequerirModificationDgrtt(BaseTransition):
    label = "Requérir modification / complément"
    from_states = [EN_VERIFICATION, EN_INSTRUCTION]
    to_state = EN_EDITION

    def precondition(self, workflow):
        return workflow.actor_is_contact_labco()

    def apply(self, workflow, data):
        if data.get("resoumission"):
            workflow.set_value("validee_hierarchie", False)
            workflow.set_value("signatures", [])

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
        ask_for_revalidation = workflow.get_value("validee_hierarchie")
        return get_form(ask_for_revalidation=ask_for_revalidation, require_note=True)


class ConfirmerRecevabiliteDgrtt(BaseTransition):
    label = "Confirmer recevabilité"
    from_states = [EN_VERIFICATION]
    to_state = EN_INSTRUCTION

    def precondition(self, workflow):
        return workflow.actor_is_contact_labco()

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
        return get_form(with_no_infolab=True)

    def message(self, workflow):
        demande = workflow.case
        tpl = (
            "Recevabilité confirmée par {actor} (contact). "
            "No Infolab: %s." % demande.no_infolab
        )
        return tpl


class ConfirmerFinalisationDgrtt(BaseTransition):
    label = "Confirmer finalisation"
    from_states = [EN_INSTRUCTION]
    to_state = TRAITEE

    def precondition(self, workflow):
        return workflow.actor_is_contact_labco()

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners

    def get_form(self, workflow, **kw):
        return get_form(with_no_eotp=True)

    def apply(self, workflow, data):
        self.send_notification(workflow)
        # self.generate_docs(workflow.case)

    def send_notification(self, workflow):
        case = workflow.case
        ctx = {
            "transition": self,
            "demande": case,
            "workflow": workflow,
            "now": datetime.now(),
        }
        subject = "Finalisation de votre demande par la DR&I"
        du = case.structure.responsables
        recipients = case.owners | du
        send_email(recipients, subject, "notif-demande-finalisee.html", ctx)

    def message(self, workflow):
        demande = workflow.case
        tpl = (
            "Traitement finalisé par {actor} (contact)."
            "No eOTP: %s." % demande.no_eotp
        )
        return tpl

    # Warning: not used anymore currently
    # def generate_docs(self, demande: Demande):
    #     from labster.di import injector
    #     from labster.domain2.model.demande import DemandeRH
    #
    #     db = injector.get(SQLAlchemy)
    #
    #     if not isinstance(demande, DemandeRH):
    #         return
    #
    #     docs = list(demande.documents_generes or [])
    #
    #     def add_pj(b: bytes, name: str):
    #         from flask import current_app
    #
    #         if current_app.config.get("TESTING"):
    #             return
    #
    #         blob = Blob(b)
    #         db.session.add(blob)
    #         db.session.flush()
    #
    #         d = {
    #             "name": name,
    #             "date": datetime.utcnow().isoformat(),
    #             "blob_id": blob.id,
    #         }
    #         docs.append(d)
    #
    #     add_pj(devis_rh(demande), "Devis RH.pdf")
    #     add_pj(lettre_commande_rh(demande), "Lettre de Commande.pdf")
    #
    #     demande.documents_generes = docs


class RejeterDgrtt(BaseTransition):
    label = "Rejeter / abandonner demande"
    category = "danger"
    from_states = [EN_EDITION, EN_VALIDATION, EN_VERIFICATION, EN_INSTRUCTION]
    to_state = REJETEE
    message = "Demande rejetée / abandonnées par {actor} (contact)."

    def precondition(self, workflow):
        return workflow.actor_is_contact_labco()

    # def precondition(self, workflow):
    #     from labster.rbac import is_membre_dri, is_membre_drv
    #
    #     actor: Profile = workflow.actor
    #     case: Demande = workflow.case
    #     if is_membre_dri(actor):
    #         return True
    #
    #     if is_membre_drv(actor, case.structure):
    #         return True
    #
    #     for structure in case.get_structure_concernees():
    #         if is_membre_drv(actor, structure):
    #             return True
    #
    #     return False

    def get_users_to_notify(self, workflow, old_state):
        case = workflow.case
        return case.owners

    def apply(self, workflow, data):
        self.send_notification(workflow)

    def send_notification(self, workflow: Workflow):
        case = workflow.case
        ctx = {
            "transition": self,
            "demande": case,
            "workflow": workflow,
            "now": datetime.now(),
        }
        subject = "Rejet de votre demande par la DR&I ou la DRV"
        send_email(case.owners, subject, "notif-demande-rejetee.html", ctx)

    def get_form(self, workflow, **kw):
        return get_form(require_note=True)


class Commenter(BaseTransition):
    label = "Envoyer un message"
    category = "success"
    from_states = [EN_EDITION, EN_VERIFICATION, EN_INSTRUCTION]
    message = "{actor} a posté le commentaire ou la question suivante: "

    def precondition(self, workflow: Workflow):
        actor = workflow.actor
        demande = workflow.case
        if workflow.state == EN_EDITION and not demande.contact_labco:
            return False
        stakeholders = self._get_stakeholders(workflow)
        return actor in stakeholders

    def get_users_to_notify(self, workflow, old_state):
        return self._get_stakeholders(workflow)

    def _get_stakeholders(self, workflow: Workflow) -> Container:
        from flask_sqlalchemy import SQLAlchemy

        from labster.di import injector
        from labster.domain2.model.profile import Profile

        db = injector.get(SQLAlchemy)

        demande: Demande = workflow.case
        stakeholders = set(demande.owners)
        if demande.contact_labco:
            stakeholders.add(demande.contact_labco)

        # FIXME
        # structure: Structure = demande.structure
        # directeurs = structure.get_directeurs()
        # for directeur in directeurs:
        #     stakeholders.add(directeur)

        for history_item in demande.wf_history:
            actor_id = history_item["actor_id"]
            if actor_id:
                # TODO
                if isinstance(actor_id, int):
                    actor = db.session.query(Profile).filter_by(old_id=actor_id).first()
                else:
                    actor = db.session.query(Profile).get(actor_id)
                if actor:
                    stakeholders.add(actor)

        return stakeholders

    def get_form(self, workflow, **kw):
        return get_form(require_note=True)

    def apply(self, workflow: Workflow, data: dict):
        self.send_notification(workflow)

    def send_notification(self, workflow: Workflow) -> None:
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
