from __future__ import annotations

from datetime import datetime

import pytz
from abilian.core.models import IdMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from labster.extensions import db

from .demandes import Demande
from .profiles import Profile


class Notification(IdMixin, db.Model):
    __tablename__ = "notification"

    created_at = Column(DateTime, default=datetime.utcnow)

    body = Column(Unicode, nullable=False)

    user_id = Column(Integer, ForeignKey(Profile.id))
    user = relationship(Profile, foreign_keys=[user_id])  # type: Profile

    actor_id = Column(Integer, ForeignKey(Profile.id))
    actor = relationship(Profile, foreign_keys=[actor_id])  # type: Profile

    demande_id = Column(Integer, ForeignKey(Demande.id))
    demande = relationship(Demande, foreign_keys=[demande_id])  # type: Demande

    sent = Column(Boolean)

    @property
    def created_at_tz(self):
        paris = pytz.timezone("Europe/Paris")
        return paris.localize(self.created_at)
