"""Main blueprint."""
from __future__ import annotations

from flask import Blueprint, render_template

from labster.security import login_required

blueprint = Blueprint("main", __name__, url_prefix="")
route = blueprint.route

__all__ = ()


@route("/")
@login_required
def home() -> str:
    return render_template("v3.j2")
