"""Formulaire PI."""
from __future__ import annotations

from labster.domain.services.constants import get_constant
from labster.newforms.base import HTML, Boolean2Field, BooleanField, \
    DateField, FieldSet, Form, IntegerField, ListeAutresDeclarations, \
    ListeContrats, ListeLicencesExistantes, Select2Field, StringField, \
    TextAreaField
from labster.newforms.common import laboratoire
from labster.newforms.pi_common import exploitation, porteur_de_projet

_CLASSES_PRODUIT_STR = """
10000 LOGICIEL SYSTÈME
- 10100 Systèmes d’exploitation
- 10200 Transmission de données
- 10300 Bases de données (SGBD)
- 10400 Langage de programmation
- 10500 Langage adapté à l’utilisateur final
- 10600 Assistance pour le développement
- 10700 Gestion d’exploitation de système
- 10800 Utilitaire
20000 LOGICIEL UNIVERSEL
- 20100 Planification / Gestion
- 20200 Comptabilité
- 20300 Personnel / Salaires
- 20400 Ventes / Inventaire
- 20500 Production
- 20600 Conception / étude / projet
- 20700 Prévision / Statistique / Analyse
- 20800 Bureautique
- 20900 Ingénierie d’information
- 21000 Traitement d’images
- 21100 EAO
30000 LOGICIEL SPECIALISE
- 30100 Agriculture
- 30200 Eaux et Forêts
- 30300 Pêche
- 30400 Exploitation minière
- 30500 Construction
- 30600 Production
- 30605 Alimentation
- 30610 Textile et habillement
- 30615 Bois, pâte et papier
- 30620 Publication et impression
- 30625 Chimie et industries dérivées
- 30630 Produits en pierre, argile et verre
- 30635 Produits métalliques
- 30640 Machines et Matériels
- 30645 Machines électriques
- 30650 Matériels de transport
- 30700 Fourniture électricité/gaz/chaleur/eau
- 30705 Electricité
- 30710 Gaz
- 30715 Fourniture d’eau
- 30800 Transport / Communication
- 30805 Transport
- 30810 Communication
- 30900 Ventes / Restaurants et débits de boissons
- 30905 Vente en gros
- 30910 Vente au détail
- 30915 Restaurants et débits de boissons
- 31000 Activités financières et d’assurances
- 31005 Activités bancaires et fiduciaires
- 31010 Courtage financier
- 31015 Assurances
- 31100 Immobilier
- 31200 Services
- 31205 Location
- 31210 Hôtels et auberges
- 31215 Radiodiffusion et publicité
- 31220 Services d’information
- 31225 Services divers
- 31230 Médecine, santé et sanitaire
- 31235 Education et recherche scientifique
- 31300 Services publics
- 31400 Loisirs et vie familiale
- 31500 Autres
40000 MULTIMEDIA / BASES DE DONNEES
- 40100 Reproduction numérique d’une œuvre 2D (peinture, photo, texte,...)
- 40200 Reproduction numérique d’œuvre 3D
- 40300 Reproduction numérique d’image animée
- 40400 Reproduction numérique d’un son
- 41000 CREATION NUMERIQUE
- 41100 Création numérique 2D
- 41200 Création numérique 3D
- 41300 Création d’une image animée
- 41400 Création numérique d’un son
- 41500 Création d’une photo numérique
- 42000 SITE WEB
"""

CLASSES_PRODUIT = _CLASSES_PRODUIT_STR.strip().split("\n")

#
# Fieldsets
#
description_oeuvre = FieldSet(
    "description_oeuvre",
    "Description de l'œuvre",
    [
        StringField("intitule", "Intitulé de l’œuvre", required=True),
        StringField("acronyme", "Acronyme", required=True),
        StringField("numero_version", "Numéro de version de l'œuvre", required=True),
        DateField("date_version", "Date de la version", required=True),
        IntegerField("nbre_lignes_code", "Nombre de lignes de code"),
        StringField("nationalite", "Nationalité de l'œuvre", required=True),
    ],
)

CHOICES1 = [
    "Logiciel (code source)",
    "Logiciel (code objet)",
    "Base de données",
    "Autre",
]

CHOICES_ORIGINALITE = [
    "logiciel premier (logiciel qui a été intégralement développé, sans utilisation de code préexistant)",
    "logiciel composé (logiciel qui incorpore tout ou partie d’un logiciel préexistant)",
    "logiciel dérivé (adaptation d’un logiciel préexistant, par exemple une version d’un programme pour un client spécifique ou portage d’un logiciel d’un environnement à un autre",
]

type_oeuvre = FieldSet(
    "type_oeuvre",
    "Type de l'œuvre",
    [
        Select2Field("type_oeuvre", "L'œuvre est", choices=CHOICES1),
        StringField("precision_type_oeuvre", "Précisez", required=True),
        Select2Field("originalite", "S'agit-il d'un", choices=CHOICES_ORIGINALITE),
        StringField(
            "logiciel_compose_details",
            "Indiquez les composants intégrés",
            required=True,
        ),
        StringField(
            "logiciel_derive_details",
            "Indiquez de quel logiciel il découle",
            required=True,
        ),
        StringField("domaine_application", "Domaine d’application", required=True),
        Select2Field(
            "classe_produit",
            "Classe de produit",
            choices=CLASSES_PRODUIT,
            required=True,
        ),
    ],
)

description_technique = FieldSet(
    "description_technique",
    "Description technique",
    [
        StringField(
            "langage_de_programmation", "Langage de programmation", required=True
        ),
        StringField(
            "outils_de_developpement", "Outils de développement", required=True
        ),
        BooleanField("cle_logique", "Clé logique/moyen cryptographique", required=True),
        HTML(
            """Joignez en PJ un schéma de l’architecture du logiciel, en indiquant les
            zones fonctionnelles, les différents modules et les modules
            facultatifs au bon fonctionnement du logiciel le cas échéant
            (avec l'onglet <b>Pièces à joindre</b>, une fois que vous avez enregistré le formulaire).
            """
        ),
        TextAreaField(
            "environnement",
            "Décrivez l’environnement du logiciel et ses interactions éventuelles avec d’autres logiciels/matériels (forge, GitHub, intégration continue, etc.).",
            required=True,
        ),
    ],
)

divulgation = FieldSet(
    "divulgation",
    "Divulgation",
    [
        BooleanField(
            "code_publie",
            "Le code source/objet a-t-il été publié, communiqué, mis en ligne ou fait l’objet d’un dépôt&nbsp;?",
            required=True,
        ),
        TextAreaField(
            "precision_code_publie",
            "Veuillez préciser",
            note="Joindre une copie des publications (avec l'onglet <b>Pièces à joindre</b>, une fois que vous aurez enregistré le formulaire).",
            required=True,
        ),
        BooleanField(
            "communication_prevue",
            "Est-ce qu’une communication relative à l’œuvre est prévue ?",
            required=True,
        ),
        TextAreaField(
            "precision_communication_prevue",
            "Veuillez préciser le type de communication et la date prévue",
            note="Joindre une copie du projet de communication (avec l'onglet <b>Pièces à joindre</b>, une fois que vous aurez enregistré le formulaire).",
            required=True,
        ),
    ],
)

contexte_contractuel = FieldSet(
    "contexte_contractuel",
    "Contexte contractuel et propriété intellectuelle",
    [
        BooleanField(
            "contrats",
            "Les travaux de recherche à l’origine de l’œuvre ont-ils été conduits dans le cadre de contrat ou partenariat de recherche ?",
            note="Par exemple financement Sorbonne Université et/ou CNRS, partenariat académique, contrat de recherche avec un partenaire privé, sponsoring, CIFRE, ANR, contrat européen, financement industriel, ministère, régional, OSEO, association, fondation, chaire…",
            required=True,
        ),
        ListeContrats(
            "liste_contrats", "Liste des contrats/partenariats", required=True
        ),
        #
        BooleanField(
            "autres_declarations",
            "L’œuvre est-elle liée à une autre (ou plusieurs) déclaration(s) d’invention ou de logiciel/base de données?",
            required=True,
        ),
        ListeAutresDeclarations(
            "liste_autres_declarations", "Liste des autres déclarations", required=True
        ),
        #
        BooleanField(
            "licences_existantes",
            "Y-a-t-il des licences existantes (licences propriétaires, licences libres, nom de la licence et n° de version de la licence)",
            required=True,
        ),
        ListeLicencesExistantes(
            "liste_licences_existantes", "Liste des licences existantes", required=True
        ),
        # TODO
    ],
)

pieces_a_joindre = FieldSet(
    "pieces_a_joindre",
    "Pièces à joindre",
    [
        HTML(
            """
    <p>Ce formulaire doit être accompagné de la "fiche individuelle de contributeur", remplie par chaque contributeur.</p>

    <p><a href="http://www.upmc.fr/modules/resources/download/default/espace_personnels/DGRTT/TRANSFERER/FICHE_INDIVIDUELLE_CONTRIBUTEUR_LOGICIEL_160915.docx">Téléchargez la fiche</a>, remplissez-la et envoyez-la à chaque contributeur afin qu'il la remplisse aussi et la signe.</p>

    <p>Une fois que vous avez enregistré le formulaire, utilisez l'onglet <b>Pièces à joindre</b> pour accompagner votre demande des documents suivants :</p>

    <ul>
        <li>une fiche individuelle de contributeur par contributeur</li>
    </ul>

    <p>et si nécessaire :</p>

    <ul>
        <li>un schéma de l'architecture du logiciel</li>
        <li>une copie des publications</li>
        <li>une copie du projet de communication</li>
    </ul>
    """
        )
    ],
)

engagement = FieldSet(
    "engagement",
    "Engagement de l'interlocuteur privilégié de l'invention",
    [
        Boolean2Field(
            "engagement",
            "En tant que porteur du projet, je reconnais accepter d’être le contact scientifique pour l’œuvre auprès de Sorbonne Université, et de la SATT LUTECH le cas échéant, au nom de l’ensemble des contributeurs, et confirme la validité des renseignements indiqués dans cette déclaration de logiciel/base de données.",
            required=True,
        )
    ],
)


#
# The Form
#
class DemandePiLogicielForm(Form):
    name = "pi_logiciel"
    template = "newforms/newform.html"
    label = "Déclaration de logiciel / base de données"

    fieldsets = [
        laboratoire,
        porteur_de_projet,
        description_oeuvre,
        type_oeuvre,
        description_technique,
        divulgation,
        contexte_contractuel,
        exploitation,
        engagement,
        pieces_a_joindre,
    ]

    def post_init(self):
        """Populate form messages from json constants."""
        conditions = get_constant("pi_logiciel.conditions")
        self.conditions = conditions
