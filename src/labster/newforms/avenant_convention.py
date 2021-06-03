"""Formulaire Avenant Convention."""
from __future__ import annotations

from labster.newforms.base import HTML, BooleanField, DateField, FieldSet, \
    Form, IntegerField, ListePartenaires, Select2Field, StringField, \
    TextAreaField
#
# Fieldsets
#
from labster.newforms.common import contributeurs, laboratoire, \
    structures_concernees
from labster.newforms.convention import CHOICES2

porteur_de_projet = FieldSet(  #
    "porteur_de_projet",
    "Porteur de projet",
    [Select2Field("porteur", "Porteur de projet", choices=[], required=True)],
)

contrat = FieldSet(  #
    "contrat",
    "Contrat",
    [
        HTML("<p>Sur quel contrat porte l’avenant ?</p>"),
        StringField("nom_projet", "Nom ou acronyme du projet", required=True),
        StringField("eotp_ou_no_dgrtt", "eOTP ou № DR&I", required=True),
        Select2Field(
            "type_financeur", "Type de financeur", required=True, choices=CHOICES2
        ),
        BooleanField(
            "integre_entreprise",
            "Le projet intègre-t-il une entreprise&nbsp;?",
            required=True,
        ),
        #
        HTML(
            "<p>Votre demande concerne la modification... (plusieurs choix possibles)</p>"
        ),
        #
        BooleanField("montant", "Du montant"),
        IntegerField("nouveau_montant", "Indiquez les modifications du montant"),
        HTML(
            "<div class='row'><div class='col-md-offset-4 col-md-8'>Vous pouvez aussi modifier le calcul du coût complet du contrat avec l’onglet <b>Feuille de coût</b> ou joindre une nouvelle annexe financière avec l’onglet <b>Pièces à joindre</b></div></div>",
            name="message_montant",
        ),
        #
        BooleanField("duree", "De la durée"),
        DateField("nouvelle_date_fin", "Nouvelle date de fin"),
        #
        BooleanField("programme_scientifique", "Du programme scientifique"),
        HTML(
            "<div class='row'><div class='col-md-offset-4 col-md-8'>Utilisez l’onglet <b>Pièces à joindre</b> pour déposer le nouveau projet scientifique</div></div>",
            name="message_programme_scientifique",
        ),
        #
        BooleanField("consortium", "Du consortium"),
        BooleanField("retirer_partenaires", "Retirer un/des partenaire(s)"),
        TextAreaField("partenaires_a_retirer", "Partenaires à retirer"),
        BooleanField("ajouter_partenaires", "Ajouter un/des partenaire(s)"),
        ListePartenaires(
            "partenaires_a_ajouter", "Partenaires à ajouter", required=False
        ),
        BooleanField("modifier_partenaires", "Modifier un/des partenaire(s)"),
        ListePartenaires(
            "partenaires_a_modifier", "Partenaires à modifier", required=False
        ),
        #
        BooleanField("autre", "Autre"),
        TextAreaField("autre_precisez", "Précisez"),
    ],
)

commentaires = FieldSet(  #
    "commentaires",
    "Commentaires",
    [
        HTML(
            """
<p>Vous pouvez indiquer dans ce champs des éléments complémentaires nécessaires à l’instruction de votre demande.</p>
<p><em>Par exemple : besoin de recruter dès le démarrage du projet ; ce nouveau contrat s’inscrit-il dans un MTA et NDA existant, etc.</em></p>"""
        ),
        TextAreaField("commentaires", "Commentaires"),
    ],
)


#
# The Form
#
class DemandeAvenantConventionForm(Form):
    template = "newforms/newform.html"
    name = "avenant_convention"
    label = "Avenant à une convention de recherche"

    fieldsets = [
        laboratoire,
        porteur_de_projet,
        structures_concernees,
        contributeurs,
        #
        contrat,
        commentaires,
    ]
