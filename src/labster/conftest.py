"""Configuration and injectable fixtures for Pytest."""
from __future__ import annotations

import logging
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pytest import fixture
from sqlalchemy.exc import SQLAlchemyError

from labster.app import create_app
from labster.domain.services.constants import get_initial_constants
from labster.extensions import db as _db

if "TYPECHECK" in os.environ:
    from typeguard import install_import_hook

    install_import_hook("labster")

    # checker = TypeChecker("labster")
    #
    # logging.captureWarnings(True)
    # if not checker.active:
    #     checker.start()


class TestConfig:
    TESTING = True
    CSRF_ENABLED = False
    MAIL_SENDER = "test@example.com"
    MAIL_SUPPRESS_SEND = True
    SECRET_KEY = "changeme"
    SERVER_NAME = "localhost.localdomain"
    SQLALCHEMY_DATABASE_URI = "sqlite://"


@fixture(scope="session")
def app() -> Flask:
    """We usually only create an app once per session."""

    return create_app(TestConfig)


@fixture
def app_context(app: Flask):
    with app.app_context() as ctx:
        yield ctx


@fixture
def request_context(app: Flask):
    with app.test_request_context() as ctx:
        yield ctx


@fixture
def db(app: Flask) -> SQLAlchemy:
    """Return a fresh db for each test."""

    with app.app_context():
        cleanup_db(_db)
        _db.create_all()

        yield _db

        _db.session.remove()
        cleanup_db(_db)

        _db.session.flush()


@fixture
def db_session(db: SQLAlchemy):
    """Kept for historical reasons."""

    return db.session


@fixture
def config():
    from labster.domain.models.config import Config

    DATA = get_initial_constants()
    config = Config()
    config.data = DATA
    return config


@fixture
def client(app, db):
    """Return a Web client, used for testing, bound to a DB session."""
    return app.test_client()


@fixture
def injector(app):
    from labster.di import injector

    return injector


#
# Cleanup utilities
#
def cleanup_db(db):
    """Drop all the tables, in a way that doesn't raise integrity errors."""

    for table in reversed(db.metadata.sorted_tables):
        try:
            db.session.execute(table.delete())
        except SQLAlchemyError:
            print(f"Failed to delete table {table}")
            pass
