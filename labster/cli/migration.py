from __future__ import annotations

import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

from labster.boot.main import main as boot
from labster.di import injector
from labster.domain2.model.structure import StructureRepository


@click.command()
@with_appcontext
def migrate_to_21():
    """Migrate from 2.0 to 2.1."""

    boot()

    fix_repo()
    db = injector.get(SQLAlchemy)
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
                # struct.is_dirty = True
                repo.delete(struct)
                repo.put(struct)
