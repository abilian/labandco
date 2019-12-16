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
            "options": [{"value": x[0], "text": x[0],} for x in types_demandes],
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
            "options": [{"value": x[0], "text": x[0],} for x in financeurs],
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
            "options": [{"value": x[0], "text": x[0],} for x in types_recrutement],
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
            + [{"value": str(p.id), "text": p.full_name,} for p in porteurs],
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
    equipe_ids = (
        db.session.query(StatsLine.equipe_id)
        .filter(StatsLine.equipe_id != None)
        .distinct()
        .all()
    )
    departement_ids = (
        db.session.query(StatsLine.departement_id)
        .filter(StatsLine.departement_id != None)
        .distinct()
        .all()
    )
    labo_ids = (
        db.session.query(StatsLine.labo_id)
        .filter(StatsLine.labo_id != None)
        .distinct()
        .all()
    )
    ufr_ids = (
        db.session.query(StatsLine.ufr_id)
        .filter(StatsLine.ufr_id != None)
        .distinct()
        .all()
    )
    pole_ids = (
        db.session.query(StatsLine.pole_id)
        .filter(StatsLine.pole_id != None)
        .distinct()
        .all()
    )

    user = get_current_profile()
    if user.has_role(Role.RESPONSABLE, "*"):
        structures = mes_structures(user)

    else:
        ids = labo_ids + departement_ids + equipe_ids + ufr_ids + pole_ids
        structure_ids = [x[0] for x in ids]
        query = db.session.query(Structure)
        structures = [query.get(id) for id in structure_ids]

    def path(structure):
        keys = ["pole", "ufr", "laboratoire", "departement", "equipe"]
        path = []
        for key in keys:
            value = getattr(structure, key)
            if value:
                path.append(value.nom)
            else:
                path.append("")
        return path

    to_sort = [(path(structure), structure) for structure in structures]
    to_sort.sort()
    structures = [t[1] for t in to_sort]

    def make_label(structure):
        prefix = "-" * structure.depth
        return f"{prefix}{structure.nom} ({structure.type})"

    return [{"value": "", "text": "-"}] + [
        {"value": str(s.id), "text": make_label(s)} for s in structures
    ]
