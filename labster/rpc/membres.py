from __future__ import annotations

from typing import Dict, List

from jsonrpcserver import method

from labster.blueprints.util import sort_by_name
from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileId, ProfileRepository
from labster.domain2.model.structure import Structure, StructureId, \
    StructureRepository
from labster.domain2.services.roles import Role, RoleService
from labster.persistence import Persistence
from labster.rpc.users import get_roles_dto_for_user
from labster.types import JSON

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
persistence = injector.get(Persistence)


@method
def get_membres(structure_id: str) -> JSON:
    structure = structure_repo.get_by_id(StructureId(structure_id))
    assert structure

    membres = role_service.get_users_with_given_role(Role.MEMBRE, structure)
    membres = sort_by_name(membres)
    membres = [m for m in membres if m.active]

    membres_dto = [serialize_membre(m, structure) for m in membres]
    return membres_dto


@method
def get_membres_rattaches_selector(structure_id: str) -> JSON:
    structure = structure_repo.get_by_id(StructureId(structure_id))
    assert structure

    membres = role_service.get_users_with_given_role(Role.MEMBRE_RATTACHE, structure)
    membres = sort_by_name(membres)

    value = [{"id": m.id, "label": m.name} for m in membres]

    all_users = list(profile_repo.get_all())
    all_users.sort(key=lambda u: (u.nom, u.prenom))

    options = [{"id": u.id, "label": u.name} for u in all_users]
    return {"selector": {"value": value, "options": options}}


@method
def update_membres_rattaches(structure_id: str, values: List[Dict]):
    structure = structure_repo.get_by_id(StructureId(structure_id))
    assert structure

    membres: List[Profile] = role_service.get_users_with_given_role(
        Role.MEMBRE_RATTACHE, structure
    )

    current_membre_ids = {m.id for m in membres}
    updated_membre_ids = {m["id"] for m in values}

    membres_to_add = updated_membre_ids.difference(current_membre_ids)
    for user_id in membres_to_add:
        user = profile_repo.get_by_id(ProfileId(user_id))
        role_service.grant_role(user, Role.MEMBRE_RATTACHE, structure)

    membres_to_remove = current_membre_ids.difference(updated_membre_ids)
    for user_id in membres_to_remove:
        user = profile_repo.get_by_id(ProfileId(user_id))
        role_service.ungrant_role(user, Role.MEMBRE_RATTACHE, structure)

    persistence.save()


#
# Util
#
def serialize_membre(membre, structure):
    roles_for_user = role_service.get_roles_for_user(membre)

    structures: List[Structure] = sort_by_name(roles_for_user[Role.MEMBRE])

    r1 = role_service.has_role(membre, Role.MEMBRE_AFFECTE, structure)
    r2 = role_service.has_role(membre, Role.MEMBRE_RATTACHE, structure)
    membre_direct = r1 or r2

    structures_dto = serialize_structures(structures)
    roles_dto = get_roles_dto_for_user(membre, base_structure=structure)

    return {
        "id": membre.id,
        "prenom": membre.prenom,
        "nom": membre.nom,
        "structures": structures_dto,
        "membre_direct": membre_direct,
        "affecte": membre.affectation == structure.dn,
        "roles": roles_dto,
    }


def serialize_structures(structures):
    return [
        {
            "id": s.id,
            "type": s.type_name,
            "name": s.sigle_ou_nom,
            "roles": [Role.MEMBRE.value],
        }
        for s in structures
    ]
