from __future__ import annotations

from datetime import datetime
from typing import Dict

from abilian.app import db
from marshmallow import Schema, fields

from labster.blueprints.util import get_current_user
from labster.domain.models.notifications import Notification

from .. import route


class DemandeSchema(Schema):
    id = fields.String()
    nom = fields.String()
    icon_class = fields.String()


class NotificationSchema(Schema):
    created_at = fields.DateTime()
    date = fields.Function(lambda obj: obj.created_at.date())
    body = fields.String()
    demande = fields.Nested(DemandeSchema)


@route("/user/timeline")
def timeline() -> Dict:
    user = get_current_user()

    notifications = Notification.query.get_for_user(user)
    notifications_dto = NotificationSchema().dump(notifications, many=True).data

    user.date_derniere_notification_vue = datetime.utcnow()
    db.session.commit()

    ctx = {"notifications": notifications_dto}
    return ctx
