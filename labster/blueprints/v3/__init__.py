"""API blueprint (for SPA)"""
from __future__ import annotations

# from flask import Blueprint
from flask_smorest import Blueprint

from labster.security import login_required

blueprint = Blueprint("v3", __name__, url_prefix="/v3/api")
route = blueprint.route

__all__ = ("route",)


@blueprint.before_request
@login_required
def before_request() -> None:
    # Do nothing, just require login
    pass


@blueprint.record
def configure(state):
    from . import user
