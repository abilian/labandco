from __future__ import annotations

from collections.abc import Collection

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy.orm import Session

from labster.domain2.model.demande import Demande, DemandeRepository
from labster.infrastructure.repositories.sqla.mappers import Mapper

# types_demande = [cls._type.value for cls in _REGISTRY.values()]


class SqlaDemandeRepository(DemandeRepository):
    session: Session

    @inject
    def __init__(self, db: SQLAlchemy, mapper: Mapper):
        self.db = db
        self.session = db.session

    def query(self):
        return self.session.query(Demande)

    def get_all(self) -> Collection[Demande]:
        return set(self.query().all())

    def put(self, demande: Demande):
        # if not demande.id:
        #     demande.id = DemandeId.new()
        self.session.add(demande)
        self.session.flush()

    def clear(self):
        self.query().delete()
