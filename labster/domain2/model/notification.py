from __future__ import annotations

from datetime import datetime

import pytz
from abilian.core.models import IdMixin
from flask_sqlalchemy import BaseQuery
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, \
    String, Unicode
from sqlalchemy.orm import relationship

from labster.extensions import db

from .demande import Demande
from .profile import Profile


class NotificationQuery(BaseQuery):
    def get_for_user(self, user, page=0):
        # TODO: paging
        # FIXME
        return (
            self.filter(Notification.user == user)
            .order_by(Notification.created_at.desc())
            .limit(25)
            .all()
        )


class Notification(IdMixin, db.Model):
    __tablename__ = "v3_notifications"
    query_class = NotificationQuery

    created_at = Column(DateTime, default=datetime.utcnow)

    body = Column(Unicode, nullable=False)

    user_id = Column(String(36), ForeignKey(Profile.id))
    user = relationship(Profile, foreign_keys=[user_id])

    actor_id = Column(String(36), ForeignKey(Profile.id))
    actor = relationship(Profile, foreign_keys=[actor_id])

    demande_id = Column(Integer, ForeignKey(Demande.id))
    demande = relationship(Demande, foreign_keys=[demande_id])

    sent = Column(Boolean, default=False)

    @property
    def created_at_tz(self):
        paris = pytz.timezone("Europe/Paris")
        return paris.localize(self.created_at)
