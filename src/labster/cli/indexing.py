""""""
from __future__ import annotations

import click
from abilian.core.extensions import db
from flask.cli import with_appcontext
from tqdm import tqdm

from labster.domain2.model.demande import Demande
from labster.extensions import whoosh

STOP = object()
COMMIT = object()


@click.command()
@click.option("--clear/--no-clear")
@with_appcontext
def reindex(clear: bool):
    """Reindex all content; optionally clear index before.

    :param clear: clear index content.
    """
    reindex_demandes()


def reindex_demandes():
    demandes = db.session.query(Demande).all()
    writer = whoosh.index.writer()
    for demande in tqdm(demandes, disable=None):
        whoosh.index_object(demande, writer)

    writer.commit()
