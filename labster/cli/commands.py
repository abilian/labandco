""""""
from __future__ import annotations

import os
import sys
from pathlib import Path
from pprint import pprint

import click
import structlog
from abilian.services import audit_service, index_service
from flask import current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

from labster.bi.synchro import sync_all
from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.roles import RoleService
from labster.domain.models.demandes import Demande
from labster.ldap2 import sync

logger = structlog.get_logger()

profile_repository = injector.get(ProfileRepository)
db = injector.get(SQLAlchemy)


#
# Development commands
#
@click.command()
@click.option("--server", default="flask")
@with_appcontext
def devserver(server):
    if server == "flask":
        web_cmd = "flask run"
    elif server == "gunicorn":
        web_cmd = "gunicorn -w1 --timeout 300 --bind 0.0.0.0:5000 'app:app'"
    elif server == "uvicorn":
        web_cmd = "uvicorn --host 0.0.0.0 --port 5000 --wsgi 'app:app'"
    else:
        raise click.BadParameter("No such server")

    daemons = [("web", web_cmd), ("webpack", "yarn --cwd front run serve")]
    run_daemons(daemons)


def run_daemons(daemons):
    import honcho.manager

    root = (Path(current_app.root_path) / "..").resolve()
    if not (root / ".git").exists():
        print(f"root = {root}")
        print("project must be installed in development mode")
        sys.exit(1)

    manager = honcho.manager.Manager()
    for name, cmd in daemons:
        manager.add_process(name, cmd, cwd=str(root))

    manager.loop()
    sys.exit(manager.returncode)


@click.command()
@with_appcontext
def config():
    config = current_app.config
    print("Current config:")
    print()
    pprint(dict(config))
    print("Current env:")
    pprint(dict(os.environ))


@click.command()
@with_appcontext
def dump_structures():
    structure_repo = injector.get(StructureRepository)
    structures = structure_repo.get_all()
    for s in structures:
        print(s.nom)
        print("Children:", s.children)
        print("Parents:", s.parents)
        print()


#
# Production commands
#
@click.command()
@with_appcontext
def create_tables():
    print("# Creating tables")
    db.create_all()


@click.command()
@with_appcontext
def create_new_tables():
    print("# Creating new tables")

    table_names = db.metadata.tables.keys()
    for name in table_names:
        if name.startswith("v3_"):
            print(f"Dropping {name}")
            db.engine.execute(f"drop table if exists {name};")

    db.create_all()


@click.command()
@with_appcontext
def ldap_sync():
    print("# Synchro LDAP")
    audit_service.stop(ignore_state=True)
    index_service.stop(ignore_state=True)

    sync.sync_users()

    db.session.commit()


@click.command()
@with_appcontext
def update_roles():
    print("# Updating roles")
    audit_service.stop(ignore_state=True)
    index_service.stop(ignore_state=True)

    sync.update_roles()

    db.session.commit()


@click.command()
@with_appcontext
def show_roles():
    users = list(profile_repository.get_all())
    users.sort(key=lambda x: (x.nom, x.prenom))
    role_service = injector.get(RoleService)
    for user in users:
        print(user)
        roles = role_service.get_roles_for_user(user)
        pprint(dict(roles))
        print()


@click.command()
@with_appcontext
def daily():
    print("# syncing LDAP")
    ldap_sync()
    print("# updating syncing BI data")
    syncbi()
    print("# updating 'retards'")
    update_retard()


@click.command()
@with_appcontext
def syncbi():
    sync_all()


@click.command()
@with_appcontext
def update_retard():
    demandes = Demande.query.all()
    for demande in demandes:
        demande.update_retard()

    db.session.commit()
