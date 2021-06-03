from __future__ import annotations

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from labster.di import injector
from labster.domain2.model.notification import Notification
from labster.rpc.registry import context_for
from labster.security import get_current_profile
from labster.types import JSONDict

db = injector.get(SQLAlchemy)


@context_for("timeline")
def timeline() -> JSONDict:
    user = get_current_profile()

    notifications = Notification.query.get_for_user(user)
    notifications_dto = NotificationSchema().dump(notifications, many=True).data

    user.date_derniere_notification_vue = datetime.utcnow()
    db.session.commit()

    ctx = {"notifications": notifications_dto}
    return ctx


class DemandeSchema(Schema):
    id = fields.String()
    nom = fields.String()
    icon_class = fields.String()


class NotificationSchema(Schema):
    created_at = fields.DateTime()
    date = fields.Function(lambda obj: str(obj.created_at.date()))
    body = fields.String()
    demande = fields.Nested(DemandeSchema)
