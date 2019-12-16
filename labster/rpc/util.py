from __future__ import annotations

from werkzeug.exceptions import Forbidden

from labster.domain2.services.roles import Role
from labster.security import get_current_profile, get_current_user


def ensure_role(role: Role):
    user = get_current_user()
    if user.is_anonymous:
        return

    profile = user.profile
    if not profile.has_role(role):
        raise Forbidden()
