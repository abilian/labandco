from __future__ import annotations

import threading
from typing import Any

from jsonrpcserver import method
from marshmallow import Schema, fields

from labster.di import injector
from labster.domain2.model.notification import Notification
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.constants import get_constant, get_constants
from labster.domain2.services.demande import get_demande_types_for_user
from labster.domain2.services.roles import Role
from labster.menu import get_menu
from labster.rbac import is_membre_dri, is_membre_drv
from labster.security import get_current_profile
from labster.types import JSONDict

from .demandes_tables import mes_taches, mes_taches_en_retard
from .home_boxes import get_boxes

structure_repo = injector.get(StructureRepository)

cache = threading.local()


@method
def get_user_context() -> JSONDict:
    user = get_current_profile()
    return get_context(user)


def get_context(user: Profile) -> JSONDict:
    menus = get_menu(user)
    types_demandes = list(get_demande_types_for_user(user))

    is_responsable = user.has_role(Role.RESPONSABLE, "*")
    is_porteur = user.has_role(Role.PORTEUR, "*")
    is_gestionnaire = user.has_role(Role.GESTIONNAIRE, "*")

    message_dgrtt = get_constant("message_dgrtt", "OK")

    return {
        "menu": [menu.asdict() for menu in menus],
        "user": UserSchema().dump(user).data,
        "types_demandes": types_demandes,
        "home_boxes": get_boxes(),
        "archives_boxes": get_boxes(archives=True),
        "is_admin": user.has_role(Role.ADMIN_CENTRAL),
        "is_membre_dri": is_membre_dri(user),
        "is_membre_drv": is_membre_drv(user),
        "is_responsable": is_responsable,
        "is_porteur": is_porteur,
        "is_gestionnaire": is_gestionnaire,
        "message_dgrtt": message_dgrtt,
        "constants": get_constants(),
    }


class UserSchema(Schema):
    nom = fields.String()
    prenom = fields.String()
    uid = fields.String()
    id = fields.String()
    login = fields.String()

    is_admin = fields.Method("get_is_admin")
    roles = fields.Method("get_roles")

    nb_notifications_non_vues = fields.Method("get_nb_notifications_non_vues")
    nb_taches = fields.Method("get_nb_taches")
    nb_taches_retard = fields.Method("get_nb_taches_retard")

    def get_is_admin(self, user: Profile):
        return user.has_role(Role.ADMIN_CENTRAL)

    def get_roles(self, user: Profile) -> list[Any]:
        assert isinstance(user, Profile)
        return []

    def get_nb_notifications_non_vues(self, user: Profile) -> int:
        date = user.date_derniere_notification_vue

        query = Notification.query.filter(Notification.user == user)
        if date:
            query = query.filter(Notification.created_at > date)

        return query.count()

    def get_nb_taches_retard(self, user: Profile) -> int:
        return len(mes_taches_en_retard(user))

    def get_nb_taches(self, user: Profile) -> int:
        return len(mes_taches(user))
