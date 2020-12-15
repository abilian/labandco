"""Champs communs à plusieurs formulaires."""
from __future__ import annotations

from labster.newforms.base import FieldSet, Select2Field
from labster.newforms.base.fields import MultipleSelect2Field

laboratoire = FieldSet(  #
    "laboratoire",
    "Structure demandeuse",
    [
        Select2Field(
            "laboratoire",
            "Nom de la structure demandeuse",
            choices=[],
            required=True,
            editable=True,
        )
    ],
)

porteur = FieldSet(  #
    "porteur",
    "Porteur de la demande",
    [Select2Field("porteur", "Porteur de la demande", choices=[], required=True)],
)

structures_concernees = FieldSet(  #
    "structures_concernees",
    "Structures concernées",
    [
        MultipleSelect2Field(
            "structures_concernees", "Structures concernées", choices=[]
        )
    ],
)

contributeurs = FieldSet(  #
    "contributeurs",
    "Contributeurs autorisés à prendre la main sur la demande",
    [MultipleSelect2Field("contributeurs", "Contributeurs", choices=[])],
)
