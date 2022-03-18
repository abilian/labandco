from __future__ import annotations

from flask import render_template
from flask_mail import Message

from labster.extensions import mail


def send_notification(user, body: str, workflow):
    """
    :param user: user to notify
    :param body: message body (HTML)
    :param workflow:

    :return: the notification object
    """
    raise RuntimeError

    # from labster.domain2.model.notification import Notification
    #
    # notification = Notification(
    #     user=user, body=body, demande=workflow.case, actor=workflow.actor
    # )
    # try:
    #     app = db.get_app()
    # except RuntimeError:
    #     app = None
    # if app:
    #     db.session.add(notification)
    #
    # if user.preferences_notifications in (FLUX_TENDU, None):
    #     notification.sent = True
    #     send_notification_by_email(notification)
    #
    # return notification


# def send_notification_by_email(notification) -> None:
#     user = notification.user
#     subject = "Une action a été réalisée sur une de vos demandes Lab&Co"
#     recipients = [user.email]
#     ctx = {
#         "notification": notification,
#         "demande": notification.demande,
#         "now": datetime.now(),
#     }
#     html = render_template("emails/notif-generique.html", **ctx)
#     msg = Message(subject, recipients=recipients, html=html)
#     mail.send(msg)


def send_email(recipients, subject, template, context):
    if not isinstance(recipients, list):
        recipients = [recipients]

    recipients = [r.email for r in recipients]
    html = render_template("emails/" + template, **context)
    msg = Message(subject, recipients=recipients, html=html)
    mail.send(msg)
