"""Formulaires PI: parties communes."""
# Nom
# Prénom
# Téléphone
# Mail
# Nationalité / Nationality
# Adresse personnelle (n°, rue, bâtiment, CP, ville, pays) / personal address
# "Part contributive en % / Contributive share - représente le pourcentage
# de participation à la création, qui conditionne le futur intéressement des contributeurs"
# Période à laquelle vous avez contribué à l'œuvre / period in which you contributed to the work
# Indiquer la nature de la contribution à l'œuvre / Please indicate the contribution to the work
from __future__ import annotations

from labster.newforms.base import Boolean2Field, BooleanField, FieldSet, \
    Select2Field, StringField, TextAreaField

interlocuteur_privilegie = FieldSet(
    "interlocuteur_privilegie",
    "Interlocuteur privilégié",
    [
        Select2Field(
            "interlocuteur_privilegie",
            "Interlocuteur privilégié",
            choices=[],
            required=True,
        ),
        StringField("nationalite", "Nationalité / Nationality", required=True),
        TextAreaField(
            "adresse_personnelle",
            "Adresse personnelle (n°, rue, bâtiment, CP, ville, pays) / personal address",
            required=True,
        ),
        StringField(
            "part_contributive",
            "Part contributive en % / Contributive share - <em>représente le pourcentage de participation à la création, qui conditionne le futur intéressement des contributeurs</em>",
            required=True,
        ),
        StringField(
            "periode_contribution",
            "Période à laquelle vous avez contribué à l'œuvre / period in which you contributed to the work",
            required=True,
        ),
        TextAreaField(
            "nature_contribution",
            "Indiquer la nature de la contribution à l'œuvre / Please indicate the contribution to the work",
            required=True,
        ),
    ],
)

porteur_de_projet = FieldSet(  #
    "porteur_de_projet",
    "Porteur de projet",
    [
        Select2Field(
            "porteur",
            "Porteur de projet",
            choices=[],
            required=True,
            note="Il s'agit de préférence d'un personnel permanent de Sorbonne Université qui sera l’interlocuteur privilégié de Sorbonne Université et de la SATT LUTECH, le cas échéant.",
        )
    ],
)

exploitation = FieldSet(
    "exploitation",
    "Exploitation",
    [
        BooleanField(
            "negociations",
            "L’œuvre fait-elle l’objet ou a-t-elle fait l’objet de négociations pour son utilisation et/ou son exploitation (par un organisme de recherche ou par un industriel) ?",
            required=True,
        ),
        TextAreaField(
            "precision_negociations",
            "Précisez l’organisme de recherche ou l’industriel, le contexte, la nature du contrat",
        ),
    ],
)

engagement = FieldSet(
    "engagement",
    "Engagement de l'interlocuteur privilégié de l'invention",
    [
        Boolean2Field(
            "engagement",
            "En tant que porteur du projet, je reconnais accepter d’être le contact scientifique pour l’œuvre auprès de Sorbonne Université, et de la SATT LUTECH le cas échéant, au nom de l’ensemble des contributeurs et confirme la validité des renseignements indiqués dans cette déclaration de logiciel/base de données.",
            required=True,
        )
    ],
)
