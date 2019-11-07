""""""
from __future__ import annotations

import json
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit

import requests
import structlog
from flask import Flask, Request, abort, flash, g, redirect, render_template, \
    session, url_for
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import Unauthorized

from labster.domain.models.profiles import Profile
from labster.domain.services.roles import get_all_users
from labster.extensions import db, login_manager

from . import route

logger = structlog.get_logger()


@login_manager.unauthorized_handler
def unauthorized(app: Flask, request: Request):
    accept_header = request.headers.get("Accept", "")
    if "application/json" in accept_header or app.testing:
        abort(401)

    return cas_login(app.config["CAS_SERVER"])


#
# Routes
#
@route("/login")
def login():
    current_user: Profile = g.current_user
    if current_user.is_authenticated:
        return render_template("auth/redirect.j2")
    else:
        return render_template("auth/login_cas.j2")


@route("/login", methods=["POST"])
def login_post():
    if "current_user" in session:
        del session["current_user"]
    return redirect(url_for(".login", _external=True))


@route("/go")
def go(app: Flask, request: Request):
    accept_header = request.headers.get("Accept", "")
    if "application/json" in accept_header or app.testing:
        abort(401)

    return cas_login(app.config["CAS_SERVER"])


@route("/callback")
def callback(app: Flask, request: Request):
    ticket = request.args.get("ticket", "")
    default_url = url_for(".login", _external=True)
    next_url = request.args.get("next", default_url)
    if not login_with_ticket(ticket, app.config["CAS_SERVER"]):
        login_manager.unauthorized()

    return redirect(next_url)


@route("/backdoor")
def backdoor(app: Flask, request: Request):
    config = app.config

    if not (config.get("ALLOW_BACKDOOR") or app.testing):
        raise Unauthorized()

    uid = request.args.get("uid", "poulainm")
    user = get_user(uid)
    login_user(user)

    if "text/html" in request.headers.get("accept", ""):
        home_url = url_for(".login", _external=True)
        return redirect(home_url)
    else:
        return "", 201


@route("/switch", methods=["GET", "POST"])
def switch(app: Flask, request: Request):
    user = g.current_user

    config = app.config
    testing = config.get("TESTING", False)

    if not testing and (user.is_anonymous or not user.has_role("alc")):
        raise Unauthorized()

    uid = request.args.get("uid", None)

    if uid:
        try:
            current_user = Profile.query.get_by_uid(uid)
        except NoResultFound:
            flash(f"Utilisateur {uid} inconnu.", "danger")
            return redirect(url_for(".login", _external=True))

        if not current_user.active:
            flash(f"Utilisateur {uid} inactif.", "danger")
            return redirect(url_for(".login", _external=True))

        session["current_user_id"] = current_user.id
        session["current_user"] = current_user.uid
        return redirect(url_for(".login", _external=True))

    else:
        all_users = get_all_users()
        chercheurs = [u for u in all_users if u.has_role("recherche")]
        ctx = {"all_users": all_users, "chercheurs": chercheurs}
        return render_template("auth/login.j2", **ctx)


#
# Util
#
def cas_login(cas_server: str):
    url = urljoin(cas_server, "login")
    scheme, netloc, path, query, fragment = urlsplit(url)
    args = parse_qs(query)
    args["service"] = [url_for("auth.callback", _external=True)]
    query = urlencode(args, doseq=True)
    url = urlunsplit((scheme, netloc, path, query, fragment))
    return redirect(url)


def login_with_ticket(ticket: str, cas_server: str):
    url = urljoin(cas_server, "p3/serviceValidate")
    service_url = url_for("auth.callback", _external=True)
    params = {"service": service_url, "ticket": ticket, "format": "JSON"}
    session = requests.Session()
    r = session.get(url, params=params)

    r.raise_for_status()

    if r.status_code != 200:
        logger.debug(
            "Error during CAS ticket validation:\nresponse code: %d"
            '\nContent: """\n%s\n"""',
            r.status_code,
            r.content,
        )
        raise ValueError(
            f"Error during CAS ticket validation reponse code: {r.status_code}"
        )
    service_response = r.json()["serviceResponse"]

    if "authenticationSuccess" not in service_response:
        # TODO: get attr "code" for details
        logger.debug(r.content)
        raise Unauthorized()

    auth_data = service_response["authenticationSuccess"]

    # Note: this is the "old" uid
    uid = auth_data["user"]
    attributes = auth_data["attributes"]

    if uid == "fermigier":
        uid = "poulainm"

    # FIXME: uid is not the "new" uid (which is attributes["uid"])
    try:
        user = get_user(uid)
    except NoResultFound:
        user = Profile(uid=uid)
        user.nom = attributes["sn"]
        user.prenom = attributes["givenName"]
        user.roles = attributes["eduPersonAffiliation"]

        db.session.add(user)

    login_user(user)
    user.cas_entry = json.dumps(attributes)
    user.date_last_login = datetime.utcnow()

    db.session.commit()
    return redirect(url_for(".login", _external=True))


def get_user(uid) -> Profile:
    return Profile.query.get_by_uid(uid)


def login_user(user):
    session["current_user_id"] = user.id
    session["current_user"] = user.uid

    logger.info("User has logged in", login=user.uid)
