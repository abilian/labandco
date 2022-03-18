from __future__ import annotations

import os
import socket
from datetime import timedelta
from typing import Any

from abilian.web.action import Endpoint
from flask.cli import load_dotenv

load_dotenv()


HOST_MAP = {
    "orophin": "TIRETDEV",
    "tareg": "PREPROD",
    "zirak": "PRODUCTION",
}

DEFAULT_SRC = [
    "'self'",
    "https://cdn.ckeditor.com/",
    "https://unpkg.com",
    "https://maxcdn.bootstrapcdn.com",
]

CONTENT_SECURITY_POLICY = {
    "default-src": DEFAULT_SRC,
    "script-src": DEFAULT_SRC
    + [
        "'unsafe-inline'",
        "'unsafe-eval'",
        "https://sentry.io/",
        "https://browser.sentry-cdn.com/",
    ],
    "connect-src": DEFAULT_SRC
    + [
        "https://sentry.io/",
    ],
    "style-src": DEFAULT_SRC + ["'unsafe-inline'"],
    "img-src": DEFAULT_SRC + ["'unsafe-inline'", "data:"],
    "font-src": DEFAULT_SRC + ["'unsafe-inline'", "data:"],
}

DEV_CONTENT_SECURITY_POLICY = {"default-src": ["'*'"], "script-src": ["'*'"]}


class DefaultConfig:
    NAME = "DEFAULT"
    PRODUCTION = False

    # FIXME later
    WTF_CSRF_ENABLED = False

    CONTENT_SECURITY_POLICY = CONTENT_SECURITY_POLICY

    # Flask config
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SECRET_KEY = "tototiti"

    # abilian-core config
    SITE_NAME = "Lab&Co Sorbonne Université"
    PRIVATE_SITE = False
    MAIL_ASCII_ATTACHMENTS = True
    ANTIVIRUS_CHECK_REQUIRED = True
    LOGO_URL = Endpoint("static", filename="img/logo_carre_32px.jpg")
    FAVICO_URL = Endpoint("static", filename="img/logo-su-square.png")

    MAIL_SENDER = "noreply@sorbonne-universite.fr"
    MAIL_SUPPRESS_SEND = True

    CELERYBEAT_SCHEDULE: dict[Any, Any] = {}
    #     # Executes every day at 6 A.M
    #     "add-every-monday-morning": {
    #         "task": "tasks.add",
    #         "schedule": crontab(hour=6, minute=0),
    #     }
    # }

    # Babel config
    BABEL_ACCEPT_LANGUAGES = ("fr",)
    BABEL_DEFAULT_TIMEZONE = "Europe/Paris"

    # Celery config
    REDIS_URI = "redis://localhost:6379/1"
    BROKER_URL = "redis://localhost:6379/0"
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

    # Persistence
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://localhost/labster"

    MAIL_SERVER = "localhost"

    # APISPEC_SWAGGER_URL = "/labster-api"
    # APISPEC_SWAGGER_UI_URL = "/labster-api-ui"
    OPENAPI_VERSION = "3.0.2"

    # Auth
    CAS_SERVER = "https://auth.sorbonne-universite.fr/cas/"
    ALLOW_BACKDOOR = False

    RESTHEART_URL = "http://localhost:18080/db"
    RESTHEART_AUTH = ("admin", "DfgV0UYgwdMM")

    # Logs
    LOG_DB = "data/log.db"


class DevConfig(DefaultConfig):
    NAME = "DEV"
    SERVER_NAME = "localhost:5000"

    # Relax security cookies settings (which are more stringent by default)
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    REMEMBER_COOKIE_HTTPONLY = False
    CONTENT_SECURITY_POLICY = DEV_CONTENT_SECURITY_POLICY

    # Debug
    DEBUG = True
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = False
    DEBUG_TB_PANELS = [
        "flask_debugtoolbar.panels.versions.VersionDebugPanel",
        "flask_debugtoolbar.panels.timer.TimerDebugPanel",
        "flask_debugtoolbar.panels.headers.HeaderDebugPanel",
        "flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel",
        "flask_debugtoolbar.panels.template.TemplateDebugPanel",
        # 'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
        "flask_debugtoolbar.panels.logger.LoggingPanel",
        "flask_debugtoolbar.panels.profiler.ProfilerDebugPanel",
        "abilian.services.indexing.debug_toolbar.IndexedTermsDebugPanel",
        # 'flask_debugtoolbar_lineprofilerpanel.panels.LineProfilerPanel',
    ]
    TEMPLATE_DEBUG = True
    ALLOW_BACKDOOR = True

    # SQLALCHEMY_ECHO = True


class DemoConfig(DefaultConfig):
    NAME = "DEMO"

    PRODUCTION = True
    PREFERRED_URL_SCHEME = "https"
    SERVER_NAME = "labster-dev.demo.abilian.com"

    MAIL_SUPPRESS_SEND = False
    TEST_EMAIL_ADRESS = "labandco-test@abilian.net"


class PreprodConfig(DefaultConfig):
    NAME = "PREPROD"

    PRODUCTION = True
    PREFERRED_URL_SCHEME = "https"
    SERVER_NAME = "labandco-pre.sorbonne-universite.fr"

    MAIL_SUPPRESS_SEND = False
    TEST_EMAIL_ADRESS = "labandco-test@abilian.net"


class TiretDevConfig(DefaultConfig):
    NAME = "TIRETDEV"

    PRODUCTION = True
    PREFERRED_URL_SCHEME = "https"
    SERVER_NAME = "labandco-dev.sorbonne-universite.fr"

    MAIL_SUPPRESS_SEND = False
    TEST_EMAIL_ADRESS = "labandco-test@abilian.net"


class ProdConfig(DefaultConfig):
    NAME = "PRODUCTION"
    SERVER_NAME = "labandco.sorbonne-universite.fr"

    PRODUCTION = True
    PREFERRED_URL_SCHEME = "https"
    MAIL_SUPPRESS_SEND = False

    # Debug email
    # EMAIL_CC = ['X']


CONFIG_MAP = {
    "DEV": DevConfig,
    "DEMO": DemoConfig,
    "TIRETDEV": TiretDevConfig,
    "PREPROD": PreprodConfig,
    "PRODUCTION": ProdConfig,
}


def get_config():
    env = os.environ
    name = env.get("APP_NAME", "DEV")

    # Hack
    hostname = socket.gethostname()
    if hostname in HOST_MAP:
        name = HOST_MAP[hostname]

    config_class = CONFIG_MAP.get(name)
    if not config_class:
        raise RuntimeError(f"Unknown application name: {name}")
    config = config_class()

    for k, v in os.environ.items():
        if k.startswith("APP_"):
            config_key = k[len("APP_") :]
            config_value = v
            setattr(config, config_key, config_value)

    # Override SQLALCHEMY_DATABASE_URI w/ env variables if needed
    pg_password = env.get("PG_PASSWORD", "")
    database_url = env.get("DATABASE_URL", "")
    sqlalchemy_database_uri = env.get("SQLALCHEMY_DATABASE_URI", "")

    if database_url:
        config.SQLALCHEMY_DATABASE_URI = database_url
    elif sqlalchemy_database_uri:
        config.SQLALCHEMY_DATABASE_URI = sqlalchemy_database_uri
    elif pg_password:
        db_uri = f"postgresql+psycopg2://labster:{pg_password}@localhost/labster"
        config.SQLALCHEMY_DATABASE_URI = db_uri

    return config
