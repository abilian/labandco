from __future__ import annotations

import os
import re
from copy import deepcopy

import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from tqdm import tqdm

from labster.boot import migration
from labster.boot.main import main as boot
from labster.di import injector
from labster.domain2.model.demande import _REGISTRY, Demande, DemandeRepository
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain.models.demandes import Demande as OldDemande
from labster.domain.models.unites import OrgUnit


@click.command()
@with_appcontext
def reboot():
    """Reboot from scratch (useful while developing)"""
    db = injector.get(SQLAlchemy)

    table_names = db.metadata.tables.keys()
    for name in table_names:
        print(f"Dropping table: {name}")
        db.engine.execute(f'drop table if exists "{name}" cascade;')

    print("loading existing DB dump:")
    cmd = "pg_restore -cO boot/labster.dump | psql labster"
    print(cmd)
    os.system(cmd)
    print("Done")

    cmd = "flask db upgrade"
    print(cmd)
    os.system(cmd)
    print("Done")

    _migrate_to_21()

    db.session.commit()


@click.command()
@with_appcontext
def migrate_to_21():
    """Migrate from 2.0 to 2.1."""
    _migrate_to_21()


def _migrate_to_21():
    db = injector.get(SQLAlchemy)

    boot()
    fix_repo()

    _migrate_contacts()
    _migrate_demandes()

    db.session.commit()


def fix_repo():
    repo = injector.get(StructureRepository)

    for struct in repo.get_all():
        children = struct.children
        for child in set(children):
            try:
                child2 = repo.get_by_id(child.id)
                assert child2 == child
            except KeyError:
                print(child.name)
                struct.children.remove(child)
                repo.delete(struct)
                repo.put(struct)


@click.command()
@with_appcontext
def migrate_contacts():
    _migrate_contacts()


def _migrate_contacts():
    db = injector.get(SQLAlchemy)

    print("## Migrating Contacts")
    structure_repo = injector.get(StructureRepository)
    structures = structure_repo.get_all()

    for structure in structures:
        if structure.old_id is None:
            continue

        old_ou = OrgUnit.query.get(structure.old_id)
        if not old_ou:
            continue

        migration.migrate_contacts_dgrtt(structure, old_ou)
        db.session.commit()


@click.command()
@with_appcontext
def migrate_membres():
    db = injector.get(SQLAlchemy)
    migration.migrate_membres()
    db.session.commit()


@click.command()
@with_appcontext
def migrate_demandes():
    _migrate_demandes()


def _migrate_demandes():
    db = injector.get(SQLAlchemy)
    demandes_repo = injector.get(DemandeRepository)

    print(f"## Dropping table v3_demandes")
    db.engine.execute(f"drop table if exists v3_demandes;")

    db.create_all()

    print("## Migrating Demandes")
    old_demandes = OldDemande.query.all()
    for old_demande in tqdm(old_demandes):
        new_demande = migrate_demande(old_demande)
        demandes_repo.put(new_demande)

    db.session.commit()


def migrate_demande(old_demande: OldDemande) -> Demande:
    profile_repo = injector.get(ProfileRepository)
    structure_repo = injector.get(StructureRepository)

    # print(f"type: {old_demande.type}")
    # demande = Demande()

    demande = None
    for cls in _REGISTRY.values():
        if cls._type.value == old_demande.type:
            demande = cls()
            break

    assert demande

    # pprint(sorted(vars(old_demande).keys()))
    keys = [
        "active",
        "attachments",
        "created_at",
        "data",
        "date_effective",
        "deleted_at",
        "editable",
        "feuille_cout",
        "form_state",
        "name",
        "no_eotp",
        "no_infolab",
        "nom",
        "past_versions",
        "type",
        "updated_at",
        "wf_current_owner_id",
        "wf_data",
        "wf_date_derniere_action",
        "wf_retard",
        "wf_stage_id",
        "wf_state",
        "id",
    ]
    # TODO:
    # wf_current_owner_id
    # wf_stage_id
    #
    # Not needed?
    # deleted_at

    nothing = object()
    for key in keys:
        value = getattr(old_demande, key, nothing)
        if value is not nothing:
            if hasattr(demande, key):
                setattr(demande, key, value)

    if old_demande.porteur_id:
        porteur = profile_repo.get_by_old_id(old_demande.porteur_id)
        demande.porteur = porteur

    if old_demande.gestionnaire_id:
        gestionnaire = profile_repo.get_by_old_id(old_demande.gestionnaire_id)
        demande.gestionnaire = gestionnaire

    if old_demande.contact_dgrtt_id:
        contact_dgrtt = profile_repo.get_by_old_id(old_demande.contact_dgrtt_id)
        demande.contact_labco = contact_dgrtt

    if old_demande.laboratoire:
        laboratoire = structure_repo.get_by_old_id(old_demande.laboratoire.id)
        if not laboratoire:
            print(
                f"Migration impossible de la structure pour la demande {old_demande.id} "
                f"(structure: {old_demande.structure}, labo: {old_demande.laboratoire})"
            )
        else:
            demande.structure = laboratoire

    # if old_demande.structure_id:
    #     structure = structure_repo.get_by_old_id(old_demande.structure_id)
    #     if not structure:
    #         print(
    #             f"Migration impossible pour la structure avec l'id: {old_demande.structure_id}"
    #         )
    #     else:
    #         demande.structure = structure

    old_wf_history = old_demande.wf_history
    for old_entry in old_wf_history:
        entry = deepcopy(old_entry)
        old_message = entry["message"]
        pat = r'<a href="/directory/users/(.*?)">'
        repl = r'<a href="/#/directory/users/\1">'
        message = re.sub(pat, repl, old_message)
        entry["message"] = message
        demande.wf_history.append(entry)

    return demande
