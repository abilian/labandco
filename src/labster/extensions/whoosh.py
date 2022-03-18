from __future__ import annotations

from functools import singledispatch
from pathlib import Path

from flask import Flask
from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import ID, KEYWORD, TEXT, Schema

from labster.types import JSONDict

schema = Schema(
    key=ID(unique=True),
    id=ID(stored=True),
    cls=KEYWORD(stored=True),
    name=TEXT(stored=True),
    text=TEXT(analyzer=StemmingAnalyzer()),
)


class Whoosh:
    whoosh_base: str
    app: Flask | None

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        whoosh_base = Path(app.config.get("WHOOSH_BASE", "whoosh"))

        if not whoosh_base.is_absolute():
            whoosh_base = Path(app.instance_path) / whoosh_base

        if not whoosh_base.is_dir():
            whoosh_base.mkdir(parents=True)

        self.whoosh_base = str(whoosh_base.resolve())

        if index.exists_in(self.whoosh_base):
            self.index = index.open_dir(self.whoosh_base)
        else:
            self.index = index.create_in(self.whoosh_base, schema)

    def index_object(self, obj, writer=None):
        from labster.domain2.model.demande import Demande

        @singledispatch
        def as_document(obj):
            raise NotImplementedError

        @as_document.register(Demande)
        def as_document_demande(demande: Demande) -> JSONDict:
            kw: JSONDict = {}

            indexed_values = []
            for k in ["nom", "name", "no_infolab", "no_eotp"]:
                v = getattr(demande, k)
                if v:
                    indexed_values.append(v)

            for v in demande.data.values():
                if isinstance(v, str):
                    indexed_values.append(v)

            allowed_roles_and_users: list[str] = []

            v = demande.porteur
            if v:
                indexed_values.append(v.full_name)
                allowed_roles_and_users += [f"user:{v.id}"]

            v = demande.gestionnaire
            if v:
                indexed_values.append(v.full_name)
                allowed_roles_and_users += [f"user:{v.id}"]

            # v = obj.laboratoire
            # if v:
            #     indexed_values.append(v.nom)
            #
            # v = obj.structure
            # if v:
            #     indexed_values.append(v.nom)
            #     allowed_roles_and_users += [f"org:{v.id}"]

            kw["id"] = str(demande.id)
            kw["text"] = " ".join(indexed_values)
            kw["name"] = demande.nom
            kw["cls"] = "Demande"
            kw["key"] = f"demande:{demande.id}"

            # kw["allowed_roles_and_users"] = " ".join(allowed_roles_and_users)
            return kw

        must_commit = False
        if not writer:
            writer = self.index.writer()
            must_commit = True

        document = as_document(obj)
        writer.update_document(**document)

        if must_commit:
            writer.commit()
