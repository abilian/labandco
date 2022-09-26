# Set up warnings control
from __future__ import annotations

import collections

# Monkey patching for Python 3.10
collections.MutableSequence = collections.abc.MutableSequence
collections.MutableMapping = collections.abc.MutableMapping


import logging
import warnings
from typing import Callable

import sentry_sdk
import sqlalchemy.exc
from abilian.app import Application as BaseApplication
from abilian.core.celery import FlaskCelery as BaseCelery
from abilian.core.celery import FlaskLoader as CeleryBaseLoader
from abilian.i18n import babel
from flask import Flask
from flask_injector import FlaskInjector
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from werkzeug.wsgi import ClosingIterator

from .config import get_config
from .di import injector
from .extensions import redis, whoosh
from .logging import init_logging

warnings.simplefilter("ignore", category=sqlalchemy.exc.SAWarning)
# Doesn't work, despite https://github.com/Kozea/WeasyPrint/issues/312
logging.getLogger("weasyprint").setLevel(100)

__all__ = ("create_app", "Application")


# logging.basicConfig(level=logging.INFO)
# logger = structlog.get_logger()


def create_app(config: type | None = None) -> Flask:
    app = Application("labster")
    app.wsgi_app = ReverseProxied(app.wsgi_app)

    init_config(app, config)
    init_logging(app)

    with app.app_context():
        init_extensions(app)

        # This import must happen after the injector has been set up.
        from .web import init_web

        init_web(app)

        FlaskInjector(app, injector=injector)

    from .cli import register_commands

    register_commands(app)

    # Temp

    # don't use abilian-core error handlers
    app.error_handler_spec = {}

    return app


def init_config(app: Application, config: type | None):
    if config:
        # for tests
        app.setup(config)
    else:
        app.config.from_object(get_config())
        # app.config.from_mapping()
        app.setup(None)


def init_extensions(app: Flask) -> None:
    init_sentry(app)
    redis.init_app(app)
    whoosh.init_app(app)

    # Hack: we want always french
    babel.locale_selector_func = lambda: "fr"


def init_sentry(app: Flask) -> None:
    dsn = app.config.get("SENTRY_DSN")
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=0.2,
        send_default_pii=True,
    )


# loader to be used by celery workers
class CeleryLoader(CeleryBaseLoader):
    flask_app_factory = "labster.app.create_app"


class CeleryApp(BaseCelery):
    loader_cls = CeleryLoader


celery = CeleryApp()


# TODO: remove this class
class Application(BaseApplication):
    # TODO: remove all of this
    # celery_app_cls = CeleryApp
    # script_manager = None
    # default_config = get_config()

    # TODO: remove
    # APP_PLUGINS = BaseApplication.APP_PLUGINS + ()
    APP_PLUGINS = ()


# From: http://flask.pocoo.org/snippets/35/
class ReverseProxied:
    """Wrap the application in this middleware and configure the front-end
    server to add these headers, to let you quietly bind this to a URL other
    than / and to an HTTP scheme that is different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    """

    def __init__(self, app: Callable) -> None:
        self.app = app

    def __call__(
        self, environ: dict[str, str], start_response: Callable
    ) -> ClosingIterator:
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "")
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]

        scheme = environ.get("HTTP_X_SCHEME", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)
