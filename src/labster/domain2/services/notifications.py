from __future__ import annotations

from datetime import datetime
from smtplib import SMTPException
from typing import TYPE_CHECKING

import structlog
from flask import render_template
from flask_mail import Message

from labster.extensions import db, mail

if TYPE_CHECKING:
    from labster.domain2.model.notification import Notification
    from labster.domain2.model.profile import FLUX_TENDU, Profile
    from labster.lib.workflow import Workflow


logger = structlog.get_logger()


def send_notification(user: Profile, body: str, workflow: Workflow) -> Notification:
    """
    :param user: user to notify
    :param body: message body (HTML)
    :param workflow:

    :return: the notification object
    """

    from labster.domain2.model.notification import Notification
    from labster.domain2.model.profile import FLUX_TENDU  # noqa: F811

    notification = Notification(
        user=user, body=body, demande=workflow.case, actor=workflow.actor
    )
    try:
        app = db.get_app()
    except RuntimeError:
        app = None
    if app:
        db.session.add(notification)

    if user.preferences_notifications in (FLUX_TENDU, None):
        send_notification_by_email(notification)
        notification.sent = True

    return notification


def send_notification_by_email(notification: Notification) -> None:
    user: Profile = notification.user
    subject = "Une action a été réalisée sur une de vos demandes Lab&Co"
    recipients = [user.email]
    ctx = {
        "notification": notification,
        "demande": notification.demande,
        "now": datetime.now(),
    }
    html = render_template("emails/notif-generique.html", **ctx)
    msg = Message(subject, recipients=recipients, html=html)
    try:
        mail.send(msg)
    except SMTPException as e:
        logger.error("SMTP error", e)


def send_email(recipients: set[Profile], subject: str, template, context) -> None:
    assert isinstance(recipients, set)

    recipients = [r.email for r in recipients]
    html = render_template("emails/" + template, **context)
    msg = Message(subject, recipients=recipients, html=html)
    mail.send(msg)
