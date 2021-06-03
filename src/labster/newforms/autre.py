"""Formulaire pour une DemandeAutre."""
from __future__ import annotations

from labster.newforms.base import FieldSet, Form, Select2Field, StringField, \
    TextAreaField

#
# Fieldsets
#
from .common import laboratoire

TYPE_CHOICES = [
    "Budget",
    "Plateformes: calcul des coûts complets, réalisation du tarif, passage en conseil…",
    "Convention d'hébergement de start-ups, d'associations…",
    "GDR, GIS, structures en réseaux…",
    "Autre",
]

porteur = FieldSet(  #
    "porteur",
    "Porteur Lab&Co",
    [Select2Field("porteur", "Porteur", choices=[], required=True)],
)

demande = FieldSet(  #
    "demande",
    "Demande",
    [
        StringField("titre", "Titre", required=True),
        Select2Field("type", "Type", choices=TYPE_CHOICES, required=True),
        TextAreaField("commentaire", "Commentaire"),
    ],
)


#
# The Form
#
class DemandeAutreForm(Form):
    name = "autre"
    template = "newforms/newform.html"
    label = "Autre Demande"

    fieldsets = [laboratoire, porteur, demande]
