from __future__ import annotations

from labster.domain.models.demandes import AUTRE, AVENANT_CONVENTION, \
    CONVENTION, PI_INVENTION, PI_LOGICIEL, RECRUTEMENT
from labster.newforms.base import Form

from .autre import DemandeAutreForm
from .avenant_convention import DemandeAvenantConventionForm
from .convention import DemandeConventionForm
from .pi_invention import DemandePiInventionForm
from .pi_logiciel import DemandePiLogicielForm
from .rh import DemandeRHForm

TYPE_DEMANDE_TO_FORM = {
    CONVENTION: DemandeConventionForm,
    AVENANT_CONVENTION: DemandeAvenantConventionForm,
    RECRUTEMENT: DemandeRHForm,
    PI_LOGICIEL: DemandePiLogicielForm,
    PI_INVENTION: DemandePiInventionForm,
    AUTRE: DemandeAutreForm,
}


def get_form_class_for(demande):
    return TYPE_DEMANDE_TO_FORM[demande.type]


def get_form_class_by_name(name):
    for cls in TYPE_DEMANDE_TO_FORM.values():
        if cls.name == name:
            return cls
    raise KeyError(name)
