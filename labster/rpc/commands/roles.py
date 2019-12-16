from __future__ import annotations

from typing import Dict, List

from glom import glom
from jsonrpcserver import method

from labster.auth import AuthContext
from labster.di import injector
from labster.domain2.model.profile import ProfileId, ProfileRepository
from labster.domain2.model.structure import StructureId, StructureRepository
from labster.domain2.services.roles import Role, RoleService
from labster.persistence import Persistence
from labster.rbac import check_can_edit_roles
from labster.rpc.cache import cache
from labster.types import JSON

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
auth_context = injector.get(AuthContext)
persistence = injector.get(Persistence)


@method
def add_roles(structure_id: str, profile_ids: List[str], role_id: str):
    structure = structure_repo.get_by_id(StructureId(structure_id))
    check_can_edit_roles(structure)

    for profile_id in profile_ids:
        profile = profile_repo.get_by_id(ProfileId(profile_id))
        role = Role[role_id]
        role_service.grant_role(profile, role, structure)

    persistence.save()

    cache.evict("users")
    cache.evict("structures")


@method
def delete_role(structure_id: str, profile_id: str, role_id: str):
    structure = structure_repo.get_by_id(StructureId(structure_id))
    check_can_edit_roles(structure)

    profile = profile_repo.get_by_id(ProfileId(profile_id))
    role = Role[role_id]
    role_service.ungrant_role(profile, role, structure)

    persistence.save()

    cache.evict("users")
    cache.evict("structures")


@method
def update_roles(structure_id: str, data: Dict[str, JSON]):
    structure = structure_repo.get_by_id(StructureId(structure_id))
    check_can_edit_roles(structure)

    for role_name in data:
        role = getattr(Role, role_name)

        users = role_service.get_users_with_given_role(role, structure)
        for user in users:
            role_service.ungrant_role(user, role, structure)

        values = data[role_name]
        if isinstance(values, dict):
            values = [values]
        for user_id in glom(values, ["id"]):
            user = profile_repo.get_by_id(ProfileId(user_id))
            role_service.grant_role(user, role, structure)

    persistence.save()

    cache.evict("users")
    cache.evict("structures")
