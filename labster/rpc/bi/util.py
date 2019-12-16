from __future__ import annotations

from labster.di import injector
from labster.domain2.model.profile import Profile
from labster.domain2.services.roles import Role, RoleService

role_service = injector.get(RoleService)


def mes_structures(user: Profile):
    roles = role_service.get_roles_for_user(user)
    structures = roles.get(Role.RESPONSABLE, [])
    return set(structures) | {s.descendants for s in structures}
