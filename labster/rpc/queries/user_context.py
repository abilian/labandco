from __future__ import annotations

from typing import Any, List

from jsonrpcserver import method
from marshmallow import Schema, fields

from labster.domain2.model.profile import Profile
from labster.domain2.services.demande import get_demande_types_for_user
from labster.domain2.services.roles import Role
from labster.domain.models.notifications import Notification
from labster.menu import get_menu
from labster.security import get_current_profile
from labster.types import JSONDict

from .demandes_tables import mes_taches, mes_taches_en_retard
from .home_boxes import get_boxes


@method
def get_user_context() -> JSONDict:
    current_profile = get_current_profile()

    menus = get_menu(current_profile)
    types_demandes = list(get_demande_types_for_user(current_profile))

    return {
        "menu": [menu.asdict() for menu in menus],
        "user": UserSchema().dump(current_profile).data,
        "types_demandes": types_demandes,
        "home_boxes": get_boxes(),
        "archives_boxes": get_boxes(archives=True),
        "is_admin": current_profile.has_role(Role.ADMIN_CENTRAL),
    }


class UserSchema(Schema):
    nom = fields.String()
    prenom = fields.String()
    uid = fields.String()
    id = fields.String()

    is_admin = fields.Method("get_is_admin")
    roles = fields.Method("get_roles")

    nb_notifications_non_vues = fields.Method("get_nb_notifications_non_vues")
    nb_taches = fields.Method("get_nb_taches")
    nb_taches_retard = fields.Method("get_nb_taches_retard")

    def get_is_admin(self, user: Profile):
        return user.has_role(Role.ADMIN_CENTRAL)

    def get_roles(self, user: Profile) -> List[Any]:
        assert isinstance(user, Profile)
        return []

    def get_nb_notifications_non_vues(self, user: Profile) -> int:
        return (
            Notification.query.filter(Notification.user == user)
            .filter(Notification.created_at > user.date_derniere_notification_vue)
            .count()
        )

    def get_nb_taches_retard(self, user: Profile) -> int:
        return len(mes_taches_en_retard(user))

    def get_nb_taches(self, user: Profile) -> int:
        return len(mes_taches(user))
