"""Send daily or weekly notification emails."""
from __future__ import annotations

from flask import render_template
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy

from labster.di import injector
from labster.domain2.model.demande import Demande
from labster.domain2.model.notification import Notification
from labster.domain2.model.profile import Profile
from labster.extensions import mail
from labster.rpc.queries.demandes_tables import mes_taches

db = injector.get(SQLAlchemy)


#
# Notifications (activity streams)
#
def send_notification_to(user: Profile) -> None:
    pending_notifications = get_pending_notifications(user)
    if not pending_notifications:
        return

    html = make_notification_email(user, pending_notifications)

    recipient = user.email
    subject = "Vos notifications Lab&Co"
    send_email(recipient, subject, html)

    for notification in pending_notifications:
        notification.sent = True


def make_notification_email(user: Profile, notifications: list[Notification]) -> str:
    demandes_set = {notification.demande for notification in notifications}
    demandes = sorted(demandes_set, key=lambda x: x.created_at, reverse=True)

    def get_notifications(demande: Demande) -> list[Notification]:
        return [n for n in notifications if n.demande == demande]

    ctx = {
        "demandes": demandes,
        "get_notifications": get_notifications,
    }
    return render_template("notifications/email/notifications.html", **ctx)


#
# Recaps
#
def send_recap_to(user: Profile) -> bool:
    html = make_recap_email(user)
    if not html:
        return False

    recipient = user.email
    subject = "Le point hebdomadaire sur vos demandes sur Lab&Co"
    send_email(recipient, subject, html)
    return True


def make_recap_email(user: Profile) -> str | None:
    """Returns None if nothing to send."""
    notifications = get_pending_notifications(user)

    demandes_set = set(mes_taches(user))
    has_tasks = bool(demandes_set)

    for notif in notifications:
        demandes_set.add(notif.demande)

    demandes = sorted(demandes_set, key=lambda x: x.created_at, reverse=True)

    if not demandes:
        return None

    def get_notifications(demande: Demande) -> list[Notification]:
        return [n for n in notifications if n.demande == demande]

    def get_cta(demande: Demande) -> str:
        workflow = demande.get_workflow(user)
        state = demande.get_state(user)
        if user not in state.task_owners(workflow):
            return ""

        state_id = state.id
        mapping = {
            "EN_VALIDATION": "Valider la demande",
            "EN_EDITION": "Compléter et soumettre la demande",
            "EN_VERIFICATION": "Vérifier la demande",
            "EN_INSTRUCTION": "Traiter ou rejeter la demande",
        }
        return mapping[state_id]

    ctx = {
        "demandes": demandes,
        "has_tasks": has_tasks,
        "get_notifications": get_notifications,
        "get_cta": get_cta,
    }
    return render_template("notifications/email/recap-new.html", **ctx)


#
# Util
#
def get_pending_notifications(user: Profile) -> list[Notification]:
    notifications = (
        Notification.query.filter(Notification.user == user)
        .filter(Notification.sent == False)
        .order_by(Notification.created_at)
        .all()
    )
    return notifications


def send_email(recipient, subject, html):
    msg = Message(subject, recipients=[recipient], html=html)
    mail.send(msg)
