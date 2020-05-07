""""""
from __future__ import annotations

from flask import Blueprint
from werkzeug.exceptions import Forbidden

from labster.domain2.services.roles import Role
from labster.security import get_current_profile

__all__ = ()


blueprint = Blueprint(
    "notifications", __name__, template_folder="templates", url_prefix="/notifications"
)
route = blueprint.route


@blueprint.record
def configure(state):
    from . import views


@blueprint.before_request
def check_alc_role():
    current_user = get_current_profile()
    if not current_user.has_role(Role.ADMIN_CENTRAL):
        raise Forbidden()
