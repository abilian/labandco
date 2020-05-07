from __future__ import annotations

from labster.domain2.model.demande import DemandeType
from labster.newforms.base import Form

from .autre import DemandeAutreForm
from .avenant_convention import DemandeAvenantConventionForm
from .convention import DemandeConventionForm
from .pi_invention import DemandePiInventionForm
from .pi_logiciel import DemandePiLogicielForm
from .rh import DemandeRHForm

TYPE_DEMANDE_TO_FORM = {
    DemandeType.CONVENTION.value: DemandeConventionForm,
    DemandeType.AVENANT_CONVENTION.value: DemandeAvenantConventionForm,
    DemandeType.RECRUTEMENT.value: DemandeRHForm,
    DemandeType.PI_LOGICIEL.value: DemandePiLogicielForm,
    DemandeType.PI_INVENTION.value: DemandePiInventionForm,
    DemandeType.AUTRE.value: DemandeAutreForm,
}


def get_form_class_for(demande):
    return TYPE_DEMANDE_TO_FORM[demande.type]


def get_form_class_by_name(name):
    for cls in TYPE_DEMANDE_TO_FORM.values():
        if cls.name == name:
            return cls
    raise KeyError(name)
