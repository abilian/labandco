from __future__ import annotations

from typing import Any, Dict

from flask import g

from labster.blueprints.util import get_current_user
from labster.blueprints.v3.demandes.tables import mes_taches, \
    mes_taches_en_retard
from labster.domain.models.notifications import Notification
from labster.domain.models.profiles import Profile
from labster.domain.models.roles import RoleType

from . import route


@route("/menu")
def menu() -> Dict[str, Any]:
    menus = g.menu
    menu_dto = [menu.asdict() for menu in menus]
    return {"menu": menu_dto}


@route("/ui-context")
def ui_context() -> Dict[str, Any]:
    menus = g.menu
    menu_dto = [menu.asdict() for menu in menus]
    user = get_current_user()
    is_admin = g.current_user.has_role("alc")
    user_dto = {
        "name": user.full_name,
        "nb_notifications_non_vues": nb_notifications_non_vues(user),
        "nb_taches": nb_taches(user),
        "nb_taches_retard": nb_taches_retard(user),
        "is_admin": is_admin,
        "id": user.id,
        "uid": user.uid,
    }
    return {"menu": menu_dto, "user": user_dto}


def nb_notifications_non_vues(user: Profile) -> int:
    return (
        Notification.query.filter(Notification.user == user)
        .filter(Notification.created_at > user.date_derniere_notification_vue)
        .count()
    )


def nb_taches_retard(user: Profile) -> int:
    return len(mes_taches_en_retard(user))


def nb_taches(user: Profile) -> int:
    return len(mes_taches(user))
