from __future__ import annotations

from abilian.core.entities import Entity
from sqlalchemy import Column, Unicode


class Financeur(Entity):
    __indexable__ = False

    nom = Column(Unicode, nullable=False)
    sigle = Column(Unicode, nullable=False)
    type = Column(Unicode, nullable=False)
    sous_type = Column(Unicode, nullable=False)
    classe = Column(Unicode)
    pays = Column(Unicode, nullable=False)
