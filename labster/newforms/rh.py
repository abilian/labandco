"""Formulaire RH."""
from __future__ import annotations

import re
from copy import deepcopy

from flask_sqlalchemy import SQLAlchemy

from labster.di import injector
from labster.domain2.model.structure import Structure
from labster.domain.services.constants import get_constant
from labster.newforms.base import BooleanField, DateField, EmailField, \
    FieldSet, Form, IntegerField, Select2Field, StringField, TextAreaField
from labster.newforms.common import laboratoire, structures_concernees

# acceptation_principe_recrutement = BooleanField(
#     "J'ai pris connaissance et j'accepte les principes de recrutement de Sorbonne Université",
#     validators=[required()])

db = injector.get(SQLAlchemy)

CHOICES1 = ["CDD", "Doctorant", "Bourse Marie Curie"]

CHOICES2 = [
    "Contrat initial",
    "Renouvellement",
    "Modification du contrat en cours",
    "Contrat doctoral initial",
    "Prolongation par avenant d'un contrat doctoral en cours",
    "Prolongation par CDD d'un doctorat en cours (cas particulier)",
    "Thèse medico-scientifique",
]

nature = FieldSet(
    "nature",
    "Nature et type de la demande",
    [
        Select2Field(
            "nature_du_recrutement",
            "Nature du recrutement",
            choices=CHOICES1,
            required=True,
        ),
        Select2Field(
            "type_de_demande",
            "Type de demande",
            choices=CHOICES2,
            show_if="false",
            required=True,
        ),
    ],
)


def choice6():
    ecoles_doctorales = (
        db.session.query(Structure).filter_by(type_name="École doctorale").all()
    )

    def sorter(ed):
        m = re.search("([0-9]+)", ed.nom)
        if m:
            n = int(m.group(1))
        else:
            n = 0
        return n

    ecoles_doctorales.sort(key=sorter)
    return [""] + [ed.nom for ed in ecoles_doctorales]


responsable_scientifique = FieldSet(  #
    "responsable_scientifique",
    "Responsable scientifique de la personne recrutée",
    [
        # TODO
        Select2Field(
            "ecole_doctorale", "École doctorale", choices=choice6, required=True
        ),
        Select2Field("porteur", "Nom", choices=[], required=True),
    ],
)

CHOICES3 = ["eOTP", "№ DR&I", "Notification de financement"]

CHOICES4 = ["eOTP", "№ DR&I", "1/2 allocation IFD", "Notification de financement"]

contrat = FieldSet(  #
    "contrat",
    "Contrat de recherche finançant cette demande de recrutement",
    [
        Select2Field("financement", "Financement", choices=CHOICES3, required=True),
        StringField("numero_de_financement", "Numéro du financement", required=True),
        BooleanField("co_finance", "Ce recrutement est-il co-financé&nbsp;?"),
        Select2Field("financement2", "Financement 2", choices=CHOICES4, required=True),
        StringField("numero_de_financement2", "Numéro du financement"),
        Select2Field("structure_financeuse", "Structure", choices=[]),
    ],
)

CHOICES5 = ["M.", "Mme"]

# beware, the exact strings are used in rh.js.
CHOICES_SIMILAR_EXP = [
    "Pour un post-doctorant: doctorat",
    "Pour un post-doctorant: doctorat plus 2 ans",
    "Pour un post-doctorant: doctorat plus 3 ans",
    "Pour un ingénieur, technicien ou administratif",
    "Pour un chercheur",
]

candidat = FieldSet(  #
    "candidat",
    "Candidat",
    [
        Select2Field("civilite", "Civilité", choices=CHOICES5, required=True),
        StringField("nom", "Nom", required=True),
        StringField("prenom", "Prénom", required=True),
        EmailField("email", "Mail", required=True),
        Select2Field(
            "similar_experience",
            "Expérience professionnelle",
            choices=CHOICES_SIMILAR_EXP,
            required=True,
            note="Des documents sont à joindre à votre demande. "
            "Une fois que vous l'aurez enregistrée, utilisez l'onglet "
            "<b>Pièces à joindre<b> pour consulter la liste et envoyer les "
            "documents.",
        ),
        IntegerField(
            "similar_experience_years",
            "Indiquez le nombre d'années d'expérience sur des niveaux de "
            "mission comparables",
        ),
    ],
)


def choice7():
    return get_constant("recrutement.grades")


CHOICES8 = [
    "Paris ou région parisienne",
    "Banyuls-sur-mer",
    "Roscoff",
    "Villefranche-sur-mer",
]

CHOICES9 = ["100%", "90%", "80%", "70%", "60%", "50%"]

poste = FieldSet(  #
    "poste",
    "Poste à pourvoir",
    [
        BooleanField(
            "modification_mission",
            "La modification concerne-t-elle les missions du contrat initial ?",
        ),
        StringField("fonction_du_poste", "Fonction du poste", required=True),
        Select2Field(
            "grade_correspondant",
            "Équivalent corps/grade fonction publique",
            choices=choice7,
        ),
        StringField(
            "objet_de_la_mission", "Objet de la mission / de l'étude", required=True
        ),
        Select2Field("localisation", "Localisation", choices=CHOICES8, required=True),
        Select2Field(
            "quotite_de_travail", "Quotité de travail", choices=CHOICES9, required=True
        ),
    ],
)

dates = FieldSet(  #
    "dates",
    "Dates du contrat",
    [
        DateField("date_debut", "Date de début", required=True),
        DateField("date_fin", "Date de fin", required=True),
    ],
)

autre_modification = FieldSet(  #
    "autre_modification",
    "Autre modification",
    [
        BooleanField(
            "modification_autre",
            "L’avenant modifie-t-il un autre élément du contrat initial&nbsp;?",
        ),
        TextAreaField("modification_autre_detail", "Indiquez lequel"),
    ],
)

publicite = FieldSet(  #
    "publicite",
    "Publicité",
    [
        TextAreaField(
            "publicite",
            "Comment avez-vous fait la publicité de ce poste (publication sur le "
            "site de la structure, le site de Sorbonne Université, ...)&nbsp;?",
            required=True,
        ),
        IntegerField(
            "nb_candidats_recus",
            "Combien de candidats avez-vous reçu en entretien&nbsp;?",
            required=True,
        ),
    ],
)

commentaire = FieldSet(  #
    "commentaire", "Commentaire", [TextAreaField("commentaire", "Commentaire")]
)


#
# The Form
#
class DemandeRHForm(Form):
    name = "rh"
    template = "newforms/newform.html"
    label = "Recrutement"

    def post_init(self):
        remuneration = FieldSet(  #
            "remuneration",
            "Rémunération",
            [
                BooleanField(
                    "modification_remuneration",
                    "L’avenant modifie-t-il les conditions de rémunération&nbsp;?",
                ),
                IntegerField(
                    "salaire_brut_mensuel_indicatif",
                    "Montant indicatif du salaire brut mensuel (en Euros)",
                    note=get_constant("demande_recrutement.bareme"),
                    editable=False,
                ),
                IntegerField(
                    "salaire_brut_mensuel",
                    "Montant du salaire brut mensuel (en Euros)",
                    required=True,
                ),
                TextAreaField("salaire_justification", "Justifier le salaire"),
                IntegerField(
                    "salaire_brut_mensuel_etp",
                    "Pour information, montant du brut mensuel équivalent "
                    "à un temps plein (en Euros)",
                    editable=False,
                ),
                TextAreaField("justification_du_salaire", "Justification du salaire"),
                BooleanField(
                    "indemnite_transport_en_commun", "Indemnité de transport en commun"
                ),
                IntegerField("nombre_enfants_a_charge", "Nombre d'enfants à charge"),
            ],
        )

        fieldsets = [
            nature,
            laboratoire,
            responsable_scientifique,
            structures_concernees,
            contrat,
            candidat,
            poste,
            dates,
            remuneration,
            autre_modification,
            publicite,
            commentaire,
        ]

        self.fieldsets = deepcopy(fieldsets)

        conditions = get_constant("recrutement.principes")
        self.conditions = conditions
