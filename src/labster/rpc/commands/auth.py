from __future__ import annotations

from flask import Flask
from jsonrpcserver import method
from werkzeug.exceptions import Unauthorized

from labster.blueprints.auth.cas import get_user_by_login, login_user
from labster.di import injector


@method
def backdoor(login="poulainm"):
    app = injector.get(Flask)

    if not (app.config.get("ALLOW_BACKDOOR") or app.testing):
        raise Unauthorized()

    user = get_user_by_login(login)
    login_user(user)

    return None
