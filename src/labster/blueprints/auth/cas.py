from __future__ import annotations

import json
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit

import requests
import structlog
from flask import Flask, Request, abort, redirect, render_template, request, \
    session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import Unauthorized

from labster.di import injector
from labster.domain2.model.profile import Profile
from labster.domain2.services.constants import get_constants
from labster.extensions import login_manager
from labster.security import get_current_user

from . import route

logger = structlog.get_logger()

db = injector.get(SQLAlchemy)


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
    current_user = get_current_user()

    if not current_user.is_authenticated:
        if _single_user():
            return render_template("auth/single_user.j2")
        return render_template("auth/login_cas.j2")

    return render_template("auth/redirect.j2")


def _single_user():
    if "bypass" in request.args:
        return False

    constants = get_constants()
    value = str(constants.get("single_user")).lower()
    return value in {"none", "true", "y"}


@route("/login", methods=["POST"])
def login_post():
    if "current_user_id" in session:
        del session["current_user_id"]
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
    login = auth_data["user"]
    attributes = auth_data["attributes"]

    if login == "fermigier":
        login = "poulainm"

    # FIXME: uid is not the "new" uid (which is attributes["uid"])
    user = get_user_by_login(login)

    if not user:
        raise Unauthorized()
        # user = Profile(uid=uid)
        # user.nom = attributes["sn"]
        # user.prenom = attributes["givenName"]
        # # user.roles = attributes["eduPersonAffiliation"]
        #
        # db.session.add(user)

    login_user(user)

    # TODO: add these fields to Profile
    user.cas_entry = json.dumps(attributes)
    user.date_last_login = datetime.utcnow()

    db.session.commit()
    return redirect(url_for(".login", _external=True))


def get_user_by_login(login: str) -> Profile:
    # This fixes some nasty "current transaction is aborted" bug
    db.session.commit()
    query = db.session.query(Profile).filter_by(active=True)
    user = query.filter_by(login=login).first()
    return user


def login_user(user):
    assert user.active
    session["current_user_id"] = user.id
    logger.info("User has logged in", login=user.login, uid=user.uid)
