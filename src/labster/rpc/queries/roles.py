from __future__ import annotations

from collections.abc import Collection
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from marshmallow import Schema, fields

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import Structure, StructureId, \
    StructureRepository
from labster.domain2.model.type_structure import DE, EQ, FA
from labster.domain2.services.roles import Role, RoleService
from labster.rbac import get_permissions_for_structure
from labster.security import get_current_user
from labster.types import JSON, JSONDict
from labster.util import sort_by_name

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
db = injector.get(SQLAlchemy)


@method
def get_roles(structure_id: str) -> list[dict[str, Any]]:
    structure = structure_repo.get_by_id(StructureId(structure_id))
    assert structure

    role_to_users = role_service.get_users_with_role_on(structure)

    if structure.type in {DE, EQ}:
        roles = [
            Role.RESPONSABLE,
        ]
    else:
        roles = [
            Role.SIGNATAIRE,
            Role.RESPONSABLE,
            Role.ADMIN_LOCAL,
            Role.GESTIONNAIRE,
            Role.PORTEUR,
        ]

    result: list[dict[str, Any]] = []
    for role in roles:
        role_dto = {
            "key": role.name,
            "label": role.value,
            "users": convert_users_to_dto(role_to_users[role]),
        }
        result += [role_dto]
    return result


@method
def get_role_selectors(structure_id: str) -> JSON:
    structure = structure_repo.get_by_id(StructureId(structure_id))
    assert structure

    permissions = get_permissions_for_structure(structure)
    if "P5" not in permissions:
        return []

    is_admin_central = _is_admin_central()
    is_admin_local = _is_admin_local(structure)
    is_admin_facultaire = _is_admin_facultaire(structure)

    if not (is_admin_central or is_admin_local):
        return []

    if structure.type in (DE, EQ):
        roles = [Role.RESPONSABLE]
    elif is_admin_central or is_admin_facultaire:
        roles = [
            Role.SIGNATAIRE,
            Role.RESPONSABLE,
            Role.ADMIN_LOCAL,
            Role.GESTIONNAIRE,
            Role.PORTEUR,
        ]
    else:
        roles = [
            Role.RESPONSABLE,
            Role.ADMIN_LOCAL,
            Role.GESTIONNAIRE,
            Role.PORTEUR,
        ]

    membres = get_membres(structure)
    role_to_users = role_service.get_users_with_role_on(structure)

    result: list[dict[str, Any]] = []
    for role in roles:
        users_with_role = role_to_users[role]
        multiple = role != Role.SIGNATAIRE
        value: JSON
        if multiple:
            value = [{"id": u.id, "label": u.name} for u in users_with_role]
        else:
            if users_with_role:
                u = list(users_with_role)[0]
                value = {"id": u.id, "label": u.name}
            else:
                value = None
        if role != Role.GESTIONNAIRE or not is_admin_central:
            options = [{"id": m.id, "label": m.name} for m in membres]
        else:
            all_users = (
                db.session.query(Profile)
                .filter_by(active=True)
                .order_by(Profile.nom, Profile.prenom)
                .all()
            )
            options = [{"id": m.id, "label": m.name} for m in all_users]

        selector_dto = {
            "key": role.name,
            "label": role.value,
            "value": value,
            "options": options,
            "multiple": multiple,
        }
        result += [selector_dto]

    return result


def _is_admin_central() -> bool:
    current_user = get_current_user()
    if not current_user.is_authenticated:
        return True

    profile = current_user.profile
    return profile.has_role(Role.ADMIN_CENTRAL)


def _is_admin_local(structure: Structure) -> bool:
    current_user = get_current_user()
    if not current_user.is_authenticated:
        return True

    profile = current_user.profile
    for ancestor in [structure] + structure.ancestors:
        if profile.has_role(Role.ADMIN_LOCAL, ancestor):
            return True

    return False


def _is_admin_facultaire(structure: Structure) -> bool:
    current_user = get_current_user()
    if not current_user.is_authenticated:
        return True

    profile = current_user.profile
    for ancestor in [structure] + structure.ancestors:
        if ancestor.type == FA and profile.has_role(Role.ADMIN_LOCAL, ancestor):
            return True

    return False


@method
def get_global_roles() -> JSONDict:
    def make_role_dto(role: Role) -> JSONDict:
        users_with_role = role_service.get_users_with_role(role)
        return {
            "key": role.name,
            "label": role.value,
            "users": convert_users_to_dto(users_with_role),
        }

    roles = [
        make_role_dto(Role.ADMIN_CENTRAL),
        make_role_dto(Role.FAQ_EDITOR),
    ]

    all_users = (
        db.session.query(Profile)
        .filter_by(active=True)
        .order_by(Profile.nom, Profile.prenom)
        .all()
    )
    options = [{"id": m.id, "label": m.name} for m in all_users]

    def make_selector(role: Role):
        users_with_role = role_service.get_users_with_role(role)
        value = [{"id": u.id, "label": u.name} for u in users_with_role]

        return {
            "key": role.name,
            "label": role.value,
            "value": value,
            "options": options,
            "multiple": True,
        }

    selectors = [
        make_selector(Role.ADMIN_CENTRAL),
        make_selector(Role.FAQ_EDITOR),
    ]

    return {
        "roles": roles,
        "selectors": selectors,
    }


#
# Util
#
def convert_users_to_dto(users: Collection[Profile]) -> list[JSON]:
    class ProfileSchema(Schema):
        id = fields.String()
        name = fields.String(attribute="reversed_name")

    users = sort_by_name(users)
    return ProfileSchema().dump(users, many=True).data


def get_membres(structure):
    """Retourne les membres (affectés et rattachés) et de la sous-structure
    (sans les membres affiliés)."""
    role_service = injector.get(RoleService)

    m1 = role_service.get_users_with_given_role(Role.MEMBRE_AFFECTE, structure)
    m2 = role_service.get_users_with_given_role(Role.MEMBRE_RATTACHE, structure)
    membres = list(set(m1) | set(m2))
    membres = sort_by_name(membres)
    membres = [m for m in membres if m.active]
    return membres
