from __future__ import annotations

from typing import cast

from flask_sqlalchemy import SQLAlchemy
from glom import glom
from jsonrpcserver import method
from werkzeug.exceptions import Forbidden

from labster.di import injector
from labster.domain2.model.profile import ProfileId, ProfileRepository
from labster.domain2.model.structure import StructureId, StructureRepository
from labster.domain2.services.roles import Role, RoleService
from labster.rbac import check_can_edit_roles
from labster.rpc.cache import cache
from labster.security import get_current_profile
from labster.types import JSON

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
db = injector.get(SQLAlchemy)


@method
def add_roles(structure_id: str, profile_ids: list[str], role_id: str):
    structure = structure_repo.get_by_id(StructureId(structure_id))
    check_can_edit_roles(structure)

    for profile_id in profile_ids:
        profile = profile_repo.get_by_id(ProfileId(profile_id))
        role = Role[role_id]
        role_service.grant_role(profile, role, structure)

    db.session.commit()

    cache.evict("users")
    cache.evict("structures")


@method
def delete_role(structure_id: str, profile_id: str, role_id: str):
    structure = structure_repo.get_by_id(StructureId(structure_id))
    check_can_edit_roles(structure)

    profile = profile_repo.get_by_id(ProfileId(profile_id))
    role = Role[role_id]
    role_service.ungrant_role(profile, role, structure)

    db.session.commit()

    cache.evict("users")
    cache.evict("structures")


@method
def update_roles(structure_id: str, data: dict[str, JSON]):
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
        if not values:
            continue

        for user_id in glom(values, ["id"]):
            user = profile_repo.get_by_id(ProfileId(user_id))
            role_service.grant_role(user, role, structure)

    # Cf. https://trello.com/c/bGR53cB9/33
    signataire_dto = cast(dict[str, str], data.get(Role.SIGNATAIRE.name, {}))
    if signataire_dto:
        signataire_id: str = signataire_dto["id"]
        signataire = profile_repo.get_by_id(ProfileId(signataire_id))
        role_service.grant_role(signataire, Role.RESPONSABLE, structure)

    db.session.commit()

    cache.evict("users")
    cache.evict("structures")


@method
def update_global_roles(data: dict[str, JSON]):
    user = get_current_profile()

    if not user.has_role(Role.ADMIN_CENTRAL):
        raise Forbidden

    for role_name in data:
        role = getattr(Role, role_name)

        users = role_service.get_users_with_role(role)
        for user in users:
            role_service.ungrant_role(user, role)

        values = data[role_name]
        if isinstance(values, dict):
            values = [values]
        if not values:
            continue

        for user_id in glom(values, ["id"]):
            user = profile_repo.get_by_id(ProfileId(user_id))
            role_service.grant_role(user, role)

    db.session.commit()

    cache.evict("users")
