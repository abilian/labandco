"""Modèle de case management adapté au projet Labster."""
from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from labster.lib.workflow import State, Workflow

if TYPE_CHECKING:
    from labster.domain2.model.profile import Profile

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
    label = "En cours de validation"
    label_short = "En validation"
    next_action = "Demande à considérer pour validation"

    def task_owners(self, workflow: Workflow) -> set[Profile]:
        demande = workflow.case
        assert demande

        structures_signataires = demande.structures_signataires()
        signatures = workflow.get_value("signatures") or []

        result = set()
        for structure in structures_signataires:
            if structure.id not in signatures:
                result.update(structure.responsables)

        return result


class EnVerification(State):
    label = "Recevabilité en cours de vérification"
    label_short = "En vérification"
    next_action = "Recevabilité à confirmer"

    def on_enter(self, workflow):
        workflow.set_value("ar_envoye", False)

    def task_owners(self, workflow):
        case = workflow.case
        if case.contact_labco:
            return {case.contact_labco}
        else:
            return set()


class EnInstruction(State):
    label = "En cours d'instruction par la DR&I"
    label_short = "En instruction"
    next_action = "Instruction à mener et finaliser"

    def task_owners(self, workflow):
        case = workflow.case
        if case.contact_labco:
            return {case.contact_labco}
        else:
            return set()


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
