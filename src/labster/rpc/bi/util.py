from __future__ import annotations

from labster.di import injector
from labster.domain2.model.profile import Profile
from labster.domain2.services.roles import Role, RoleService

role_service = injector.get(RoleService)


def mes_structures(user: Profile):
    roles = role_service.get_roles_for_user(user)
    structures = roles.get(Role.RESPONSABLE, [])
    result = set(structures)
    for s in structures:
        result.update(s.descendants)
    return result
