from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.roles import Role, RoleService
from labster.rpc.cache import cache

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
db = injector.get(SQLAlchemy)


@method
def update_membres_rattaches(structure_id: str, values: list[dict]):
    structure = structure_repo.get_by_id(structure_id)
    assert structure

    membres: list[Profile] = role_service.get_users_with_given_role(
        Role.MEMBRE_RATTACHE, structure
    )

    current_membre_ids = {m.id for m in membres}
    updated_membre_ids = {m["id"] for m in values}

    membres_to_add = updated_membre_ids.difference(current_membre_ids)
    for user_id in membres_to_add:
        user = profile_repo.get_by_id(user_id)
        role_service.grant_role(user, Role.MEMBRE_RATTACHE, structure)

    membres_to_remove = current_membre_ids.difference(updated_membre_ids)
    for user_id in membres_to_remove:
        user = profile_repo.get_by_id(user_id)
        role_service.ungrant_role(user, Role.MEMBRE_RATTACHE, structure)

    db.session.commit()

    cache.evict("users")
    cache.evict("structures")
