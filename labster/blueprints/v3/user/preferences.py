from __future__ import annotations

from pprint import pprint

from flask import flash, g, request

from labster.blueprints.util import get_current_user
from labster.extensions import db

from .. import route

CHOICES = [
    (0, "En flux continu (défaut)"),
    (1, "Agrégées, une fois par jour"),
    (2, "Agrégées, une fois par semaine (le jeudi)"),
]


@route("/user/preferences")
def preferences():
    user = get_current_user()

    if user.preferences_notifications is None:
        user.preferences_notifications = 0

    if user.preferences_nb_jours_notifications is None:
        user.preferences_nb_jours_notifications = 0

    return {
        "choices": CHOICES,
        "preferences_notifications": user.preferences_notifications,
        "nb_jours_notification": user.preferences_nb_jours_notifications,
    }


@route("/user/preferences", methods=["POST"])
def preferences_post():
    user = g.current_user

    payload = request.json

    pref = payload["preferences_notifications"]
    nb_jours_notification = payload["nb_jours_notification"]

    modified = False
    if pref != user.preferences_notifications:
        user.preferences_notifications = pref
        modified = True

    if nb_jours_notification != user.preferences_nb_jours_notifications:
        user.preferences_nb_jours_notifications = nb_jours_notification
        modified = True

    if modified:
        db.session.commit()
        flash("Vos préférences ont été mises à jours")

    return "", 204
