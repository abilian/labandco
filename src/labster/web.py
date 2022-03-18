from __future__ import annotations

from pathlib import Path
from typing import Callable

import pkg_resources
import structlog
from abilian.services import audit_service
from flask import Flask, current_app, g, request, session
from toolz import first, memoize
from werkzeug.utils import import_string

from labster.util import url_for

from . import search
from .bus import register_callback
from .security import get_current_user, login_user

BLUEPRINTS = [
    "labster.rpc",
    "labster.blueprints.v3",
    "labster.blueprints.main",
    "labster.blueprints.auth",
    "labster.blueprints.backup",
    "labster.blueprints.notifications",
]


def init_web(app: Flask) -> None:
    app.context_processor(inject_polymorphic_url_for)

    register_blueprints(app)

    app.before_request(login_user)
    app.before_request(stop_services)
    app.before_request(inject_debug_info)
    app.before_request(make_session_permanent)
    app.before_request(inject_assets)
    app.before_request(setup_cache)

    app.jinja_env.filters.update(datetime=lambda x: x.strftime("%d/%m/%y %H:%M"))

    search.register(app)

    register_callback()


def register_blueprints(app: Flask) -> None:
    logger = structlog.get_logger()

    for fqn in BLUEPRINTS:
        module = import_string(fqn)
        logger.info("Registering blueprint", name=module.__name__)
        app.register_blueprint(module.blueprint)


def make_session_permanent() -> None:
    session.permanent = True


def inject_debug_info() -> None:
    debug_info = {}
    current_user = get_current_user()
    if current_user.is_authenticated:
        debug_info["user_uid"] = current_user.uid
    debug_info["url"] = request.url

    g.debug_info = debug_info

    try:
        ws = pkg_resources.working_set
        version = ws.by_key["labster"]._version  # type: ignore
    except:
        version = "???"

    g.labster_version = version


def inject_assets() -> None:
    @memoize
    def get_assets_from_filesystem():
        root = Path(current_app.root_path)
        static = root / "static"
        css = static / "css"
        js = static / "js"
        start = len(str(root))
        css_assets = [
            str(first(css.glob("chunk*")))[start:],
            str(first(css.glob("app*")))[start:],
        ]
        js_assets = [
            str(first(js.glob("chunk*")))[start:],
            str(first(js.glob("app*")))[start:],
        ]
        return {"css": css_assets, "js": js_assets}

    if current_app.config.get("PRODUCTION"):
        g.assets = get_assets_from_filesystem()
    else:
        g.assets = {"css": [], "js": ["http://labster.local:8080/app.js"]}


#
# Various temporary hacks
#
def stop_services() -> None:
    # TODO later: audit service needs Users, not Profiles
    if audit_service.running:
        audit_service.stop()
        # if index_service.running:
        #     index_service.stop()


def inject_polymorphic_url_for() -> dict[str, Callable]:
    # TODO: use real registry
    return {"url_for": url_for, "id": id}


def setup_cache() -> None:
    g.cache = {}
