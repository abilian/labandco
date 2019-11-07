"""Formulaire Avenant Convention."""

from __future__ import annotations

from labster.newforms.base import FieldSet, Select2Field, StringField

#
# Fieldsets
#
laboratoire = FieldSet(  #
    "laboratoire",
    "Structure demandeuse",
    [StringField("laboratoire", "Nom de la structure demandeuse", editable=False)],
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
        Select2Field(
            "structures_concernees", "Structures concernées", choices=[], required=True
        )
    ],
)

contributeurs = FieldSet(
    "contributeurs",
    "Contributeurs autorisés à prendre la main sur la demande",
    [Select2Field("contributeurs", "Contributeurs", choices=[], required=True)],
)
