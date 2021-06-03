"""Modèle un peu simpliste de hiérarchie LDAP + info métiers spécifiques."""
from __future__ import annotations

from abilian.core.entities import Entity
from sqlalchemy import Column, Integer, Unicode


class FaqEntry(Entity):
    __tablename__ = "faq_entry"

    title = Column(Unicode, default="", nullable=False)
    category = Column(Unicode, default="", nullable=False)
    body = Column(Unicode, default="", nullable=False)
    view_count = Column(Integer, default=0)
