from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from flask import render_template
from flask_mail import Message

from labster.extensions import db, mail

if TYPE_CHECKING:
    from labster.domain.models.profiles import Profile
    from labster.domain.models.notifications import Notification
    from labster.lib.workflow import Workflow


def send_notification(user: Profile, body: str, workflow: Workflow) -> Notification:
    """
    :param user: user to notify
    :param body: message body (HTML)
    :param workflow:

    :return: the notification object
    """

    from labster.domain.models.notifications import Notification

    notification = Notification(
        user=user, body=body, demande=workflow.case, actor=workflow.actor
    )
    try:
        app = db.get_app()
    except RuntimeError:
        app = None
    if app:
        db.session.add(notification)

    if user.preferences_notifications in (0, None):
        send_notification_by_email(notification)

    return notification


def send_notification_by_email(notification: Notification) -> None:
    user = notification.user  # type: Profile
    subject = "Une action a été réalisée sur une de vos demandes Lab&Co"
    recipients = [user.email]
    ctx = {
        "notification": notification,
        "demande": notification.demande,
        "now": datetime.now(),
    }
    html = render_template("emails/notif-generique.html", **ctx)
    msg = Message(subject, recipients=recipients, html=html)
    mail.send(msg)


def send_email(recipients, subject, template, context):
    if not isinstance(recipients, list):
        recipients = [recipients]

    recipients = [r.email for r in recipients]
    html = render_template("emails/" + template, **context)
    msg = Message(subject, recipients=recipients, html=html)
    mail.send(msg)
