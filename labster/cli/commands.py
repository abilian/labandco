""""""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from pprint import pprint

import click
import structlog
from abilian.services import audit_service, index_service
from flask import current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from pampy import match

from labster.bi.synchro import sync_all
from labster.blueprints.notifications.mails import send_notification_to, \
    send_recap_to
from labster.di import injector
from labster.domain2.model.demande import Demande
from labster.domain2.model.profile import DAILY, WEEKLY, Profile, \
    ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.roles import Role, RoleService
from labster.ldap import sync
from labster.rpc.cache import cache

logger = structlog.get_logger()

profile_repository = injector.get(ProfileRepository)
db = injector.get(SQLAlchemy)
role_service = injector.get(RoleService)


#
# Development commands
#
@click.command()
@click.option("--server", default="flask")
@click.option("--coverage")
@with_appcontext
def devserver(server, coverage=False):
    if server == "flask":
        if coverage:
            flask = shutil.which("flask")
            web_cmd = f"coverage run {flask} run --no-reload"
        else:
            web_cmd = "flask run"
    elif server == "gunicorn":
        web_cmd = "gunicorn -w1 --timeout 300 --bind 0.0.0.0:5000 'wsgi:app'"
    elif server == "uvicorn":
        web_cmd = "uvicorn --host 0.0.0.0 --port 5000 --wsgi 'wsgi:app'"
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
            db.engine.execute(f'drop table if exists "{name}" cascade;')

    db.create_all()


@click.command()
@with_appcontext
def drop_all_tables():
    print("# Dropping all tables")

    table_names = db.metadata.tables.keys()
    for name in table_names:
        print(f"Dropping {name}")
        db.engine.execute(f'drop table if exists "{name}" cascade;')

    db.create_all()


@click.command()
@with_appcontext
def ldap_sync():
    print("# Synchro LDAP")
    audit_service.stop(ignore_state=True)
    index_service.stop(ignore_state=True)

    sync.sync_users()

    db.session.commit()
    cache.clear()


@click.command()
@click.option("--max", default=0)
@with_appcontext
def update_roles(max):
    print("# Updating roles")
    audit_service.stop(ignore_state=True)
    index_service.stop(ignore_state=True)

    sync.update_roles(max)

    db.session.commit()


@click.command()
@with_appcontext
def show_roles():
    users = list(profile_repository.get_all())
    users.sort(key=lambda x: (x.nom, x.prenom))
    for user in users:
        print(user)
        roles = role_service.get_roles_for_user(user)
        pprint(dict(roles))
        print()


@click.command()
@with_appcontext
def syncbi():
    print("# updating syncing BI data")
    sync_all()


@click.command()
@with_appcontext
def update_retard():
    print("# updating 'retards'")
    demandes = Demande.query.all()
    for demande in demandes:
        demande.update_retard()

    db.session.commit()


@click.command()
@click.option("-v", "--verbose", is_flag=True)
@with_appcontext
def send_recap(verbose):
    users = Profile.query.filter_by(active=True).order_by(Profile.nom).all()
    for user in users:
        status = send_recap_to(user)
        if status and verbose:
            print(f"recap sent to {user.login}")

    db.session.commit()


@click.command()
@click.argument("frequency", required=True, type=str)
@click.option("-v", "--verbose", is_flag=True)
@with_appcontext
def send_notifications(frequency, verbose=False):
    # fmt: off
    preference = match(
        frequency,
        "daily", DAILY,
        "weekly", WEEKLY,
    )
    # fmt: on
    users = (
        Profile.query.filter(Profile.active == True)
        .filter(Profile.preferences_notifications == preference)
        .order_by(Profile.nom)
        .all()
    )

    for user in users:
        if verbose:
            print(f"Sending notification to {user.login}")
        send_notification_to(user)

    db.session.commit()


@click.command()
@with_appcontext
def grant_mnp():
    user = db.session.query(Profile).filter(Profile.login == "poulainm").one()
    role_service.grant_role(user, Role.ADMIN_CENTRAL)

    db.session.commit()


@click.command()
@with_appcontext
def fix():
    # from .fixes import fix_ajout_supann_code_entite
    # fix_ajout_supann_code_entite()

    print("No fix needed")
