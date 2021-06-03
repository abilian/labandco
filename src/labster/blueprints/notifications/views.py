"""Debug views for notifictions."""
from __future__ import annotations

from flask import render_template
from flask_sqlalchemy import SQLAlchemy

from labster.di import injector
from labster.domain2.model.profile import Profile

from . import route
from .mails import get_pending_notifications, make_notification_email, \
    make_recap_email

db = injector.get(SQLAlchemy)


#
# Weekly recaps
#
@route("/debug/recaps/")
def debug_recaps():
    users = (
        db.session.query(Profile).filter_by(active=True).order_by(Profile.login).all()
    )

    users_receiving_emails = []
    for user in users:
        email = make_recap_email(user)
        if not email:
            continue
        users_receiving_emails.append(user)

    return render_template(
        "notifications/debug/recaps.html", users=users_receiving_emails
    )


@route("/debug/recaps/<id>")
def debug_recap_for(id):
    user = Profile.query.get(id)
    email = make_recap_email(user)
    if email:
        return email
    else:
        return "Pas de mail à envoyer"


#
# Notifications (activity streams)
#
@route("/debug/streams/")
def debug_streams():
    users = (
        db.session.query(Profile).filter_by(active=True).order_by(Profile.login).all()
    )

    users_receiving_emails = []
    for user in users:
        notifications = get_pending_notifications(user)
        if not notifications:
            continue
        users_receiving_emails.append(user)

    return render_template(
        "notifications/debug/notifications.html", users=users_receiving_emails
    )


@route("/debug/streams/<id>")
def debug_stream_for(id):
    user = Profile.query.get(id)
    notifications = get_pending_notifications(user)
    email = make_notification_email(user, notifications)
    if email:
        return email
    else:
        return "Pas de mail à envoyer"
