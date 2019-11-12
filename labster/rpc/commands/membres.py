from __future__ import annotations

from typing import Dict, List

from jsonrpcserver import method

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileId, ProfileRepository
from labster.domain2.model.structure import StructureId, StructureRepository
from labster.domain2.services.roles import Role, RoleService
from labster.persistence import Persistence
from labster.rpc import cache

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
persistence = injector.get(Persistence)


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

    cache.evict("users")
    cache.evict("structures")
