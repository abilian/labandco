from __future__ import annotations

from flask import Blueprint

blueprint = Blueprint("bi", __name__, template_folder="templates", url_prefix="/bi")
route = blueprint.route


@blueprint.record
def configure(state):
    from . import views
