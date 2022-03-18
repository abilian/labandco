from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method

from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.roles import Role, RoleService
from labster.rpc.queries.user import get_roles_dto_for_user
from labster.types import JSON
from labster.util import sort_by_name

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
db = injector.get(SQLAlchemy)


@method
def get_membres(structure_id: str, include_ss: bool = False) -> JSON:
    structure = structure_repo.get_by_id(structure_id)
    assert structure

    if include_ss:
        membres = role_service.get_users_with_given_role(Role.MEMBRE, structure)
    else:
        membres_affectes = role_service.get_users_with_given_role(
            Role.MEMBRE_AFFECTE, structure
        )
        membres_rattaches = role_service.get_users_with_given_role(
            Role.MEMBRE_RATTACHE, structure
        )
        membres = set(membres_affectes) | set(membres_rattaches)

    membres_tries = sort_by_name(membres)
    membres_tries = [m for m in membres_tries if m.active]

    membres_dto = [serialize_membre(m, structure) for m in membres_tries]
    return membres_dto


@method
def get_membres_rattaches_selector(structure_id: str) -> JSON:
    structure = structure_repo.get_by_id(structure_id)
    assert structure

    membres = role_service.get_users_with_given_role(Role.MEMBRE_RATTACHE, structure)
    membres = [m for m in membres if m.active]
    membres = sort_by_name(membres)

    value = [{"id": m.id, "label": m.name} for m in membres]

    all_users = list(profile_repo.get_all())
    all_users = [u for u in all_users if u.active]
    all_users.sort(key=lambda u: (u.nom, u.prenom))

    options = [{"id": u.id, "label": u.name} for u in all_users]
    return {"selector": {"value": value, "options": options}}


#
# Serialization
#
def serialize_membre(membre, structure):
    # roles_for_user = role_service.get_roles_for_user(membre)

    # structures: List[Structure] = sort_by_name(roles_for_user[Role.MEMBRE])

    r1 = role_service.has_role(membre, Role.MEMBRE_AFFECTE, structure)
    r2 = role_service.has_role(membre, Role.MEMBRE_RATTACHE, structure)
    membre_direct = r1 or r2

    # structures_dto = serialize_structures(structures)
    roles_dto = get_roles_dto_for_user(membre, base_structure=structure)

    return {
        "id": membre.id,
        "prenom": membre.prenom,
        "nom": membre.nom,
        # "structures": structures_dto,
        "membre_direct": membre_direct,
        "affecte": membre.affectation == structure.dn,
        "roles": roles_dto,
    }


# def serialize_structures(structures):
#     return [
#         {
#             "id": s.id,
#             "type": s.type_name,
#             "name": s.sigle_ou_nom,
#             "roles": [Role.MEMBRE.value],
#         }
#         for s in structures
#     ]
