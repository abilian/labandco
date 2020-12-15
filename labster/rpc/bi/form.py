from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

from labster.bi.model import StatsLine
from labster.di import injector
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.domain2.services.roles import Role
from labster.security import get_current_profile

from .util import mes_structures

db = injector.get(SQLAlchemy)


def get_selectors():
    result = []

    types_demandes = db.session.query(StatsLine.type_demande).distinct().all()
    types_demandes.sort()
    result.append(
        {
            "name": "type_demande",
            "label": "Type de demande",
            "multiple": True,
            "options": [
                {
                    "value": x[0],
                    "text": x[0],
                }
                for x in types_demandes
            ],
        }
    )

    financeurs = (
        db.session.query(StatsLine.financeur)
        .filter(StatsLine.type_demande == "Convention de recherche")
        .filter(StatsLine.financeur != None)
        .filter(StatsLine.financeur != "")
        .order_by(StatsLine.financeur)
        .distinct()
        .all()
    )
    result.append(
        {
            "name": "financeur",
            "label": "Financeur",
            "multiple": True,
            "options": [
                {
                    "value": x[0],
                    "text": x[0],
                }
                for x in financeurs
            ],
        }
    )

    types_recrutement = (
        db.session.query(StatsLine.type_recrutement)
        .filter(StatsLine.type_demande == "Recrutement")
        .filter(StatsLine.type_recrutement != None)
        .distinct()
        .all()
    )
    result.append(
        {
            "name": "type_recrutement",
            "label": "Type de recrutement",
            "multiple": True,
            "options": [
                {
                    "value": x[0],
                    "text": x[0],
                }
                for x in types_recrutement
            ],
        }
    )

    porteur_ids = (
        db.session.query(StatsLine.porteur_id)
        .filter(StatsLine.porteur_id != None)
        .distinct()
        .all()
    )
    porteurs = [db.session.query(Profile).get(id) for id in porteur_ids]
    porteurs.sort(key=lambda x: (x.nom, x.prenom))
    result.append(
        {
            "name": "porteur_id",
            "label": "Porteur",
            # "multiple": True,
            "options": [{"value": "", "text": "-"}]
            + [
                {
                    "value": str(p.id),
                    "text": p.full_name,
                }
                for p in porteurs
            ],
        }
    )

    result.append(
        {
            "name": "structure_id",
            "label": "Structure",
            # "multiple": True,
            "options": get_structure_choices(),
        }
    )
    return result


def get_structure_choices():
    l2_ids = (
        db.session.query(StatsLine.l2).filter(StatsLine.l2 != None).distinct().all()
    )
    l3_ids = (
        db.session.query(StatsLine.l3).filter(StatsLine.l3 != None).distinct().all()
    )
    l4_ids = (
        db.session.query(StatsLine.l4).filter(StatsLine.l4 != None).distinct().all()
    )
    l5_ids = (
        db.session.query(StatsLine.l5).filter(StatsLine.l5 != None).distinct().all()
    )
    l6_ids = (
        db.session.query(StatsLine.l6).filter(StatsLine.l6 != None).distinct().all()
    )

    user = get_current_profile()
    if user.has_role(Role.RESPONSABLE, "*"):
        structures = mes_structures(user)

    else:
        ids = l2_ids + l3_ids + l4_ids + l5_ids + l6_ids
        structure_ids = [x[0] for x in ids]
        query = db.session.query(Structure)
        structures = [query.get(id) for id in structure_ids]

    to_sort = [
        (structure.path + [structure.nom], structure) for structure in structures
    ]
    to_sort.sort(key=lambda x: x[0])
    structures = [t[1] for t in to_sort]

    def make_label(structure):
        prefix = "+-" * structure.depth
        return f"{prefix}{structure.nom} ({structure.type})"

    return [{"value": "", "text": "-"}] + [
        {"value": str(s.id), "text": make_label(s)} for s in structures
    ]
