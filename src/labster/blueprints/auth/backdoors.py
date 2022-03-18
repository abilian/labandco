from __future__ import annotations

import os

import structlog
from flask import Flask, Request, flash, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import Unauthorized

from labster.di import injector
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.roles import Role, RoleService
from labster.security import get_current_user
from labster.util import sort_by_name

from . import route
from .cas import get_user_by_login, login_user

logger = structlog.get_logger()
db = injector.get(SQLAlchemy)
structure_repo = injector.get(StructureRepository)
role_service = injector.get(RoleService)


#
# Routes
#
@route("/backdoor")
def backdoor(app: Flask, request: Request):
    allow_backdoor = app.config.get("ALLOW_BACKDOOR") or os.getenv("ALLOW_BACKDOOR")
    if not (allow_backdoor or app.testing):
        raise Unauthorized()

    login = request.args.get("login", "poulainm")
    user = get_user_by_login(login)
    login_user(user)

    if "text/html" in request.headers.get("accept", ""):
        home_url = url_for(".login", _external=True)
        return redirect(home_url)
    else:
        return "", 201


@route("/switch", methods=["GET", "POST"])
def switch(app: Flask, request: Request):
    user = get_current_user()
    if user.is_anonymous:
        raise Unauthorized()

    profile = user.profile

    testing = app.config.get("TESTING", False)
    if not testing and not profile.has_role(Role.ADMIN_CENTRAL):
        raise Unauthorized()

    if request.args:
        return do_switch(request.args)

    gouvernance = get_users_by_login({"chambaz"})
    gestionnaires = get_users_by_login(
        {"pulcherie", "boyern", "courtoisi", "sos", "girardv"}
    )
    porteurs = get_users_by_login(
        {"carapezzi", "duhieu", "lombard", "diasdeamorim", "valdes"}
    )
    directeurs = get_users_by_login(
        {
            "santiardbaro",
            "charretier",
            "sciandra",
            "mercierc",
            "mouchelj",
            "stemmann",
        }
    )

    dri = structure_repo.get_by_sigle("DR&I")
    membres_dri = role_service.get_users_with_given_role(Role.MEMBRE_AFFECTE, dri)
    membres_dri = sort_by_name(membres_dri)
    membres_dri_logins = [m.login for m in membres_dri if m.active]
    membres_dri = get_users_by_login(membres_dri_logins)

    groups = [
        ["Gouvernance", gouvernance],
        ["Gestionnaires", gestionnaires],
        ["Porteurs", porteurs],
        ["Directeurs", directeurs],
        ["DR&I", membres_dri],
    ]
    return render_template("auth/login.j2", groups=groups)


def do_switch(args):
    login = args.get("login", None)

    new_user = get_user_by_login(login)

    if not new_user:
        flash(f"Utilisateur {login} inconnu.", "danger")
        return redirect(url_for(".switch", _external=True))

    login_user(new_user)
    return redirect(url_for(".login", _external=True))


# Utilisé en phase de test (URL: /switch/).
def get_users_by_login(logins) -> list[Profile]:
    users = (
        db.session.query(Profile)
        .filter(Profile.login.in_(logins))
        .filter(Profile.active == True)
        .order_by(Profile.login)
        .all()
    )

    for user in users:
        roles = role_service.get_roles_for_user(user)
        values = sorted(
            r.value for r in roles.keys() if not r.value.startswith("Membre ")
        )
        user._roles = ", ".join(values)

    return users
