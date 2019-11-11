from __future__ import annotations

from typing import Any, Collection, Dict, List

from jsonrpcserver import method
from marshmallow import Schema, fields

from labster.auth import AuthContext
from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import StructureId, StructureRepository
from labster.domain2.model.type_structure import DE, EQ
from labster.domain2.services.roles import Role, RoleService
from labster.persistence import Persistence
from labster.types import JSON
from labster.util import sort_by_name

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
auth_context = injector.get(AuthContext)
persistence = injector.get(Persistence)


@method
def get_roles(structure_id: str) -> List[Dict[str, Any]]:
    # TODO: permissions
    structure = structure_repo.get_by_id(StructureId(structure_id))
    assert structure

    role_to_users = role_service.get_users_with_role_on(structure)

    if structure.is_reelle:
        roles = [
            Role.SIGNATAIRE,
            Role.RESPONSABLE,
            Role.ADMIN_LOCAL,
            Role.GESTIONNAIRE,
            Role.PORTEUR,
        ]
    else:
        roles = [Role.ADMIN_LOCAL]

    result: List[Dict[str, Any]] = []
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

    # FIXME
    if auth_context.current_user:
        is_admin_central = auth_context.current_user.has_role("alc")
        is_admin_local = False
        # TODO instead:
        # is_admin_central = role_service.has_role(g.current_profile, Role.ADMIN_CENTRAL)
        # is_admin_local = role_service.has_role(
        #     g.current_profile, Role.ADMIN_LOCAL, structure
        # )
    else:
        # For tests
        is_admin_central = True
        is_admin_local = True

    if not (is_admin_central or is_admin_local):
        return []

    if structure.type in (DE, EQ):
        roles = [Role.ADMIN_LOCAL]
    elif is_admin_local and not is_admin_central:
        roles = [
            Role.RESPONSABLE,
            Role.GESTIONNAIRE,
            Role.PORTEUR,
        ]
    else:
        roles = [
            Role.SIGNATAIRE,
            Role.RESPONSABLE,
            Role.ADMIN_LOCAL,
            Role.GESTIONNAIRE,
            Role.PORTEUR,
        ]

    membres = get_membres(structure)
    role_to_users = role_service.get_users_with_role_on(structure)

    result: List[Dict[str, Any]] = []
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
        options = [{"id": m.id, "label": m.name} for m in membres]
        selector_dto = {
            "key": role.name,
            "label": role.value,
            "value": value,
            "options": options,
            "multiple": multiple,
        }
        result += [selector_dto]

    return result


#
# Util
#
def convert_users_to_dto(users: Collection[Profile]) -> List[JSON]:
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
