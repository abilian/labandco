"""Formulaire PI."""
from __future__ import annotations

from labster.newforms.base import HTML, BooleanField, DateField, FieldSet, \
    Form, IntegerField, ListePartenaires, Select2Field, StringField, \
    TextAreaField, TriStateField
from labster.newforms.common import contributeurs, laboratoire, \
    structures_concernees

contrat = FieldSet(
    "contrat",
    "",
    [
        BooleanField(
            "lien_contrat",
            "Votre demande est-elle en lien avec un contrat&nbsp;?",
            required=True,
        ),
        StringField("eotp_ou_no_dgrtt", "eOTP ou No DR&I", required=True),
    ],
)

porteur_de_projet = FieldSet(  #
    "porteur_de_projet",
    "Porteur de projet",
    [Select2Field("porteur", "Porteur de projet", choices=[], required=True)],
)

CHOICES1 = ["Coordinateur", "Partenaire", "Sous-traitant"]
CHOICES2 = [
    "ANR",
    "Commission Européenne",
    "Entreprise",
    "Financement public national",
    "FUI",
    "Institution européenne et internationale",
    "Fondation",
    "Autre",
]
CHOICES3 = [
    "Accord de collaboration",
    "Accord de consortium",
    "Contrat de prestation",
    "autre",
]

contrat_financement = FieldSet(  #
    "contrat_financement",
    "Informations sur le contrat et son financement",
    [
        Select2Field(
            "role_upmc", "Rôle de Sorbonne Université", required=True, choices=CHOICES1
        ),
        StringField("nom_ou_acronyme", "Nom ou acronyme du projet", required=True),
        TextAreaField("description_courte", "Description courte", required=True),
        Select2Field(
            "type_financeur", "Type de financeur", required=True, choices=CHOICES2
        ),
        StringField("nom_financeur", "Nom du financeur", required=True),
        BooleanField(
            "integre_entreprise",
            "Le projet intègre-t-il une entreprise&nbsp;?",
            required=True,
        ),
        BooleanField("appel_a_projets", "Appel à projets&nbsp;?", required=True),
        Select2Field("type_contrat", "Type de contrat", choices=CHOICES3),
        DateField(
            "date_depot",
            "Date limite de dépôt ou date de début souhaité du projet",
            required=True,
        ),
        IntegerField(
            "duree_previsionnelle", "Durée prévisionnelle (en mois)", required=True
        ),
    ],
)

partenaires = FieldSet(  #
    "partenaires",
    "Partenaires",
    [
        HTML(
            "<p>Vous devez saisir au moins un partenaire, sauf s'il s'agit d’un appel à projet, auquel cas la liste des partenaires est à renseigner dans les pièces jointes et non ici.</p>"
        ),
        ListePartenaires("partenaires", "Partenaires", required=False),
    ],
)

projet_scientifique = FieldSet(  #
    "projet_scientifique",
    "Projet scientifique et contributions de la structure",
    [
        HTML(
            '<p>Les documents complémentaires (canevas d’appel à projets, annexe scientifique, annexe financière…) sont à déposer dans l\'onglet "pièces à joindre".</p>'
        ),
        HTML(
            '<p>Utilisez l\'onglet "Feuille de coût" pour effectuer le calcul du coût de votre projet.</p>'
        ),
        TextAreaField(
            "role_laboratoire",
            "Description du rôle de la structure et du résultat attendu",
        ),
        HTML("<p><b>Informations complémentaires</b></p>"),
        IntegerField("montant_financement", "Montant du financement envisagé (en €)"),
        IntegerField("nombre_recrutements", "Nombre de recrutements prévisionnels"),
    ],
)

apport_upmc = FieldSet(  #
    "apports_upmc",
    "Apports scientifiques Sorbonne Université dans le projet – Résultats",
    [
        HTML(
            "<p><em>Quelles sont les résultats antérieurs mis en œuvre dans le projet par votre équipe Sorbonne Université&nbsp;?</em></p>"
        ),
        #
        TriStateField("materiel_donnees", "Matériel / données", required=True),
        BooleanField("materiel_donnees_propre_upmc", "Propre à Sorbonne Université"),
        BooleanField(
            "materiel_donnees_obtenu_precedents_contrats",
            "Obtenu lors de précédents contrats",
        ),
        BooleanField("materiel_donnees_humains", "Humains"),
        BooleanField("materiel_donnees_infectieux", "Infectieux"),
        TextAreaField("materiel_donnees_description", "Description"),
        HTML("<hr>"),
        #
        TriStateField("savoir_faire", "Savoir-faire / expertise", required=True),
        BooleanField("savoir_faire_propre_upmc", "Propre à Sorbonne Université"),
        BooleanField(
            "savoir_faire_obtenu_precedents_contrats",
            "Obtenu lors de précédents contrats",
        ),
        TextAreaField("savoir_faire_description", "Description"),
        HTML("<hr>"),
        #
        TriStateField("logiciel", "Logiciel", required=True),
        BooleanField("logiciel_propre_upmc", "Propre à Sorbonne Université"),
        BooleanField(
            "logiciel_obtenu_precedents_contrats", "Obtenu lors de précédents contrats"
        ),
        BooleanField("logiciel_libre", "Libre"),
        TextAreaField("logiciel_description", "Description"),
        HTML("<hr>"),
        #
        TriStateField("brevet", "Brevet", required=True),
        BooleanField("brevet_propre_upmc", "Propre à Sorbonne Université"),
        BooleanField(
            "brevet_obtenu_precedents_contrats", "Obtenu lors de précédents contrats"
        ),
        TextAreaField("brevet_description", "Description"),
        HTML("<hr>"),
        #
        HTML("<p><b>Types de résultats attendus</b></p>"),
        #
        BooleanField("resultats_publication", "Publication"),
        BooleanField("resultats_brevet", "Brevet"),
        BooleanField("resultats_logiciel", "Logiciel"),
        BooleanField("resultats_autre", "Autre"),
        StringField("resultats_preciser", "Préciser"),
        HTML("<hr>"),
        #
        HTML("<p><b>À qui vont appartenir les résultats&nbsp;?</b></p>"),
        #
        BooleanField("aux_tutelles_des_labos", "Aux tutelles des structures"),
        BooleanField("aux_autres_partenaires", "Aux autres partenaires"),
        BooleanField("aux_tutelles_et_partenaires", "Aux tutelles et aux partenaires"),
    ],
)

commentaires = FieldSet(  #
    "commentaires",
    "Commentaires",
    [
        HTML(
            """
<p>Vous pouvez indiquer dans ce champs des éléments complémentaires
nécessaires à l’instruction de votre demande.</p>

<p><em>Par exemple : besoin de recruter dès le démarrage du projet ;
ce nouveau contrat s’inscrit-il dans un MTA et NDA existant, etc.</em></p>"""
        ),
        TextAreaField("commentaires", "Commentaires"),
    ],
)


#
# The Form
#
class DemandeConventionForm(Form):
    template = "newforms/newform.html"
    name = "convention"
    label = "Convention de recherche"

    fieldsets = [
        contrat,
        #
        laboratoire,
        porteur_de_projet,
        structures_concernees,
        contributeurs,
        #
        contrat_financement,
        partenaires,
        projet_scientifique,
        apport_upmc,
        commentaires,
    ]
