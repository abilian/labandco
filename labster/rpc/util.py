from __future__ import annotations

from werkzeug.exceptions import Forbidden

from labster.di import injector
from labster.domain2.services.roles import Role, RoleService
from labster.security import get_current_user

role_service = injector.get(RoleService)


def ensure_role(role: Role):
    user = get_current_user()
    if user.is_anonymous:
        return

    profile = user.profile
    if not profile.has_role(role):
        raise Forbidden()


def owner_sorter(owner):
    is_signataire = role_service.has_role(owner, Role.SIGNATAIRE, "*")
    return (-int(is_signataire), owner.nom, owner.prenom)
