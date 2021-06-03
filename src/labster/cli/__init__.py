""""""
from __future__ import annotations

import uuid

import click
import structlog
from abilian.cli import script
from flask.cli import AppGroup, FlaskGroup
from werkzeug.utils import import_string

from labster.app import create_app

# from . import commands, restheart, testing

MODULE_NAMES = ["commands", "restheart", "testing", "indexing"]


#
# Register commands and shell-level CLI
#
@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the labster application."""


def register_module(namespace, module_name):
    fqn = "labster.cli." + module_name
    try:
        module = import_string(fqn)
        namespace.update(vars(module))
    except ImportError as e:
        print(f"Failed to import module: {fqn}")
        print(e)


def register_commands(app):
    request_id = str(uuid.uuid4())
    logger = structlog.get_logger(request_id=request_id, path="[CLI]")

    logger.debug("registering commands")

    namespace = {}
    for module_name in MODULE_NAMES:
        register_module(namespace, module_name)

    app.cli.add_command(cli)
    app.cli.add_command(script)

    for _name, obj in sorted(namespace.items()):
        if isinstance(obj, (click.core.Command, AppGroup)):
            app.cli.add_command(obj)
