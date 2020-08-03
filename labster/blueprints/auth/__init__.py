"""
Auth blueprint - used for authencation.
"""
from __future__ import annotations

from flask import Blueprint

blueprint = Blueprint("auth", __name__, template_folder="templates", url_prefix="")
route = blueprint.route

__all__ = ()


@blueprint.record
def configure(state):
    from . import backdoors, cas
