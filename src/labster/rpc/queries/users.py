from __future__ import annotations

from typing import Any

import ramda as r
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from marshmallow import Schema, fields
from sqlalchemy import or_

from labster.di import injector
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.domain2.services.roles import Role, RoleService
from labster.rpc.cache import cache
from labster.types import JSONDict
from labster.util import sort_by_name

db = injector.get(SQLAlchemy)
role_service = injector.get(RoleService)


@method
@cache.memoize(tag="users", expire=3600)
def get_users(q="", page=0) -> JSONDict:
    page = int(page)
    query = (
        db.session.query(Profile)
        .filter(Profile.active == True)
        .order_by(Profile.nom, Profile.prenom)
    )
    total = query.count()

    q = q.strip()
    if q:
        query = query.filter(
            or_(Profile.nom.ilike(f"{q}%"), Profile.prenom.ilike(f"{q}%"))
        )

    query = query.offset(100 * page)
    users = query.limit(100).all()

    users_dto = ProfileSchemaMany().dump(users, many=True).data
    return {"users": users_dto, "total": total}


#
# Serialization
#
class ProfileSchemaMany(Schema):
    id = fields.String()
    nom = fields.Function(lambda obj: obj.nom.upper())
    prenom = fields.String()
    structures = fields.Method("get_structures")

    @staticmethod
    def get_structures(user):
        roles = role_service.get_roles_for_user(user)
        return make_structures_dto(roles)


def make_structures_dto(roles_dict: dict[Role, set[Structure]]) -> list[dict]:
    def reverse_dict(d: dict) -> dict[Any, list]:
        result: dict[Any, list] = {}
        for k, l in d.items():
            for v in l:
                result[v] = result.get(v, [])
                result[v].append(k)
        return result

    def make_structure_dto(structure):
        role_set = {role.value for role in structures_to_roles[structure]}
        role_set -= {"Membre", "Membre affilié"}
        if "Membre affecté" in role_set or "Membre rattaché" in role_set:
            role_set.add("Membre")
        role_set -= {"Membre affecté", "Membre rattaché"}
        roles = sorted(role_set)

        structure_dto = {
            "name": structure.sigle_ou_nom,
            "id": structure.id,
            "roles": ", ".join(roles),
            "depth": structure.depth,
        }
        return structure_dto

    structures_to_roles = reverse_dict(roles_dict)
    structures = sort_by_name(structures_to_roles.keys())
    structures_dto = r.pipe(r.map(make_structure_dto), r.filter(lambda s: s["roles"]))(
        structures
    )
    structures_dto.sort(key=lambda x: x["depth"])
    return structures_dto
