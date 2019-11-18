"""Main blueprint."""
from __future__ import annotations

from flask import Blueprint, render_template

from labster.domain.services.constants import get_constants
from labster.security import login_required

blueprint = Blueprint("main", __name__, url_prefix="")
route = blueprint.route

__all__ = ()


@blueprint.before_request
@login_required
def before_request():
    pass


@route("/")
def home() -> str:
    return render_template("v3.j2")


@route("/calculettes/feuille_cout")
def calculette_feuille_cout():
    constants = get_constants()
    model = {
        "id": None,
        "editable": True,
        "constants": constants["convention"],
        "couts_charges": constants["recrutement"]["couts_charges"],
    }
    model["constants"]["POINT_INDICE"] = constants["point_indice"]

    return render_template("calculette_feuille_cout.html", model=model)
