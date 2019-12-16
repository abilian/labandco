from __future__ import annotations

from typing import Any, Optional, Set

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy.orm import Session

from labster.domain2.model.structure import Structure, StructureId, \
    StructureRepository
from labster.infrastructure.repositories.sqla.mappers import Mapper


class SqlaStructureRepository(StructureRepository):
    session: Session

    @inject
    def __init__(self, db: SQLAlchemy, mapper: Mapper):
        self.db = db
        self.session = db.session

    def query(self):
        return self.session.query(Structure)

    def get_all(self) -> Set[Structure]:
        return set(self.query().all())

    def put(self, structure: Structure):
        if not structure.id:
            structure.id = StructureId.new()
        self.session.add(structure)
        self.session.flush()

    def delete(self, structure: Structure):
        self.session.delete(structure)
        self.session.flush()

    def is_empty(self):
        return self.query().count() == 0

    def clear(self):
        self.query().delete()
        self.session.flush()

    def get_by(self, key: str, value: Any) -> Optional[Structure]:
        return self.query().filter_by(**{key: value}).first()

    # Not needed I think
    # def get_by_id(self, id: StructureId) -> Optional[Structure]:
    #     return self.query().get(id)
    #
    # def get_by_dn(self, dn: str) -> Optional[Structure]:
    #     return self.query().filter(Structure.dn == dn).first()
