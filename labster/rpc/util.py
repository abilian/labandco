from __future__ import annotations

from werkzeug.exceptions import Forbidden

from labster.auth import AuthContext
from labster.di import injector


def ensure_role(role):
    auth_context = injector.get(AuthContext)
    if auth_context.current_user and not auth_context.current_user.has_role(role):
        raise Forbidden()
