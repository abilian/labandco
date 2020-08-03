"""
TODO: explain
"""
from __future__ import annotations

from abilian.core.entities import Entity
from abilian.core.sqlalchemy import JSONDict
from sqlalchemy import Column


class Config(Entity):
    __tablename__ = "config"
    __indexable__ = False

    data = Column(JSONDict(), default=dict)
