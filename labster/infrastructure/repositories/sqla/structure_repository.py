from __future__ import annotations

from typing import Set

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Session, backref, mapper, relationship

from labster.domain2.model.structure import Structure, StructureId, \
    StructureRepository


def make_mapper(metadata):
    hierarchy = Table(
        "v3_hierarchy",
        metadata,
        Column("parent_id", String(36), ForeignKey("v3_structures.id")),
        Column("child_id", String(36), ForeignKey("v3_structures.id")),
    )

    structures = Table(
        "v3_structures",
        metadata,
        #
        Column("id", String(36), primary_key=True),
        Column("old_id", Integer),
        Column("active", Boolean),
        Column("type_name", String),
        #
        Column("nom", String),
        Column("sigle", String),
        Column("dn", String),
        Column("old_dn", String),
        Column("email", String),
        #
        Column("permettre_reponse_directe", Boolean),
        Column("permettre_soummission_directe", Boolean),
        #
    )
    mapper(
        Structure,
        structures,
        properties={
            "children": relationship(
                Structure,
                secondary=hierarchy,
                primaryjoin=(hierarchy.c.parent_id == structures.c.id),
                secondaryjoin=(hierarchy.c.child_id == structures.c.id),
                collection_class=set,
                backref=backref("parents", collection_class=set),
            )
        },
    )


class SqlaStructureRepository(StructureRepository):
    session: Session

    @inject
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.session = self.db.session
        make_mapper(self.db.metadata)

    def get_all(self) -> Set[Structure]:
        return set(self.session.query(Structure).all())

    def put(self, structure: Structure):
        if not structure.id:
            structure.id = StructureId.new()
        self.session.add(structure)
        self.session.flush()

    def delete(self, structure: Structure):
        self.session.delete(structure)
        self.session.flush()

    def is_empty(self):
        return self.session.query(Structure).count() == 0

    def clear(self):
        self.session.query(Structure).delete()
        self.session.flush()

    def get_by_id(self, id: StructureId):
        return self.session.query(Structure).get(id)

    def get_by_dn(self, dn: str):
        return self.session.query(Structure).filter(Structure.dn == dn).first()
