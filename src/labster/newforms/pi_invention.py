"""Formulaire PI."""
from __future__ import annotations

from typing import Any

from labster.domain.services.constants import get_constant
from labster.newforms.base import HTML, Boolean2Field, BooleanField, \
    FieldSet, Form, ListeContrats, ListeDivulgationsFutures, \
    ListeDivulgationsPassees, ListeMateriels, ListePartenairesContactes, \
    StringField, TextAreaField
#
# Fieldsets
#
from labster.newforms.common import laboratoire
from labster.newforms.pi_common import porteur_de_projet

description_technique = FieldSet(
    "description_technique",
    "Description technique",
    [
        StringField("titre", "Titre de l'invention", required=True),
        HTML("<p><em>En quoi l’invention se distingue-t-elle de l’existant ?</em></p>"),
        StringField(
            "elements_distincts", "A. Eléments distincts et avantages", required=True
        ),
        #
        BooleanField(
            "publications_proches",
            "B. Avez-vous connaissance de publications proches de l'invention?",
            required=True,
        ),
        StringField(
            "publications_proches_details",
            "Indiquez la référence",
            note="Joindre une copie des publications (avec l'onglet <b>Pièces à joindre</b>, une fois que vous aurez enregistré le formulaire).",
        ),
        #
        BooleanField(
            "recherche_bases_brevets",
            "C. Une recherche dans les bases de données brevets a-t-elle été effectuée* ? ",
            required=True,
        ),
        StringField(
            "recherche_bases_brevets_detail_1",
            "Quelle(s) base(s) de données, quels mots clés et quels documents avez-vous identifiés?",
            required=True,
        ),
        StringField(
            "recherche_bases_brevets_detail_2",
            "Parmi les documents identifiés, quel est pour vous le document le plus proche de l’invention? ",
            required=True,
        ),
        StringField(
            "recherche_bases_brevets_detail_3",
            "Précisez en quoi votre invention diffère des documents cités",
            required=True,
        ),
        #
        TextAreaField(
            "limites",
            "Quelles sont pour vous les limites de mise en œuvre de l’invention et comment peuvent-elles être surmontées?",
            required=True,
        ),
        TextAreaField(
            "applications",
            "Quelles applications potentielles de l’invention avez-vous identifiées (forces/faiblesses)?",
            required=True,
        ),
        TextAreaField(
            "prochaines_etapes",
            "Quelles sont pour vous les prochaines étapes pour les développer et les valider?",
            required=True,
        ),
        #
        BooleanField(
            "depot_anterieur",
            "Avez-vous déjà déposé une déclaration d’invention dans le domaine de l’invention ou un domaine proche?",
            required=True,
        ),
        TextAreaField(
            "depot_anterieur_detail",
            "Indiquez si cette déclaration d’invention a donné lieu à des dépôts de brevet(s)ou de logiciel(s) en mentionnant leurs références (numéro de dépôt, date de dépôt, nom du déposant, titre,…) et précisez si ce(s) brevet(s)/ logiciel(s) font l’objet d’une exploitation industrielle ou commerciale",
            required=True,
        ),
        BooleanField(
            "depot_anterieur_gere_par_upmc",
            "Cette déclaration d’invention a-t-elle été gérée par Sorbonne Université?",
            required=True,
        ),
        StringField(
            "depot_anterieur_gere_par", "Précisez qui l'a gérée", required=True
        ),
    ],
)

valorisation = FieldSet(
    "valorisation",
    "Valorisation de l'invention",
    [
        BooleanField(
            "partenaires",
            "Connaissez-vous des partenaires intéressés ou susceptibles d’être intéressés pour exploiter l’invention? ",
            required=True,
        ),
        TextAreaField(
            "precision_partenaires",
            "Indiquez le nom de ces partenaires potentiels",
            required=True,
        ),
        BooleanField(
            "partenaires_contactes",
            "Avez-vous déjà contacté certaines entreprises? ",
            required=True,
        ),
        ListePartenairesContactes(
            "liste_partenaires_contactes",
            "Indiquez le nom de ces entreprises et votre contact",
            note="Joindre la copie de l'accord de secret avec l'onglet <b>Pièces à joindre</b>, une fois que vous aurez enregistré le formulaire",
            required=True,
        ),
        BooleanField(
            "creation_entreprise",
            "Envisagez-vous de valoriser votre invention à travers la création d’entreprise?",
            required=True,
        ),
        TextAreaField(
            "precision_creation_entreprise",
            "Précisez l’avancée de ce projet",
            required=True,
        ),
    ],
)

divulgation = FieldSet(
    "divulgation",
    "Divulgation",
    [
        HTML(
            """<p>Toute divulgation des résultats valorisables avant protection affecte le caractère de « nouveauté » critère indispensable.</p>

            <p>Divulgation orale ou écrite de l’invention (par exemple : discussions avec des tiers couvertes ou non par un accord de confidentialité, publication, abstract, poster ou présentation orale en congrès, séminaire, soutenances de thèse/Master/concours/HDR sans huis clos, rapport d’activité, dépôt d’une séquence dans une banque de données…</p>"""
        ),
        #
        BooleanField(
            "divulgations_passees",
            "<u>Dans le passé</u> : l’invention a-t-elle déjà fait l’objet d’une divulgation par l’équipe de recherche ou un tiers ? y compris lors de discussions informelles avec des tiers sans accord de confidentialité* ?",
            required=True,
        ),
        ListeDivulgationsPassees(
            "liste_divulgations_passees",
            "Liste des divulgations passees",
            required=True,
        ),
        #
        BooleanField(
            "divulgations_futures",
            "<u>Dans le futur</u> : l’invention doit-elle faire prochainement l’objet d’une divulgation écrite ou orale?",
            required=True,
        ),
        ListeDivulgationsFutures(
            "liste_divulgations_futures",
            "Liste des divulgations futures",
            required=True,
        ),
    ],
)

cadre_contractuel = FieldSet(
    "cadre_contractuel",
    "Cadre contractuel et financement",
    [
        BooleanField(
            "materiels",
            "Avez-vous utilisé pour vos recherches du matériel (matériel biologique, logiciel…) obtenu auprès de sociétés ou d’autres équipes de recherche?",
            required=True,
        ),
        ListeMateriels(
            "liste_materiels",
            "Liste des materiels",
            note="Joindre une copie de l’accord de transfert de matériel (MTA) correspondant avec l’onglet Pièces à joindre, une fois que vous aurez enregistré le formulaire",
            required=True,
        ),
        #
        BooleanField(
            "contrats",
            "Les travaux de recherche à l’origine de l’invention ont-ils été conduits dans le cadre de contrat ou partenariat de recherche ?",
            note="Par exemple financement Sorbonne Université et/ou CNRS, partenariat académique, contrat de recherche avec un partenaire privé, sponsoring, CIFRE, ANR, contrat européen, financement industriel, ministère, régional, OSEO, association, fondation, chaire…",
            required=True,
        ),
        ListeContrats(
            "liste_contrats", "Liste des contrats/partenariats", required=True
        ),
    ],
)

engagement = FieldSet(
    "engagement",
    "Engagement de l'interlocuteur privilégié de l'invention",
    [
        Boolean2Field(
            "engagement",
            "En tant que porteur du projet, je reconnais accepter d’être l'interlocuteur privilégié de l'invention auprès de Sorbonne Université, et de la SATT LUTECH le cas échéant, au nom de l’ensemble des contributeurs, et confirme la validité des renseignements indiqués dans cette déclaration d'invention.",
            required=True,
        )
    ],
)


#
# The Form
#
class DemandePiInventionForm(Form):
    template = "newforms/newform.html"
    name = "pi_invention"
    label = "Déclaration d'invention / déclaration de travaux valorisables"
    conditions: Any = None

    fieldsets = [
        laboratoire,
        porteur_de_projet,
        description_technique,
        divulgation,
        cadre_contractuel,
        valorisation,
        engagement,
        # pieces_a_joindre,  # added in Form.post_init
    ]

    def post_init(self):
        """Populate form messages from json constants."""
        val = get_constant("pi_invention.pieces_a_joindre")
        pieces_a_joindre = FieldSet("pieces_a_joindre", "Pièces à joindre", [HTML(val)])
        self.fieldsets += [pieces_a_joindre]

        conditions = get_constant("pi_invention.conditions")
        self.conditions = conditions
