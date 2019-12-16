"""Main blueprint."""
from __future__ import annotations

from abilian.core.models.blob import Blob
from flask import Blueprint, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound

from labster.domain.models.demandes import Demande
from labster.domain.services.constants import get_constants
from labster.rbac import check_read_access, feuille_cout_editable
from labster.security import get_current_profile, login_required

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


@route("/feuille_cout/<id>")
def feuille_cout(id, db: SQLAlchemy):
    constants = get_constants()
    constants = get_constants()

    demande = db.session.query(Demande).get(id)
    check_read_access(demande)

    model = demande.feuille_cout
    model["id"] = demande.id
    model["editable"] = feuille_cout_editable(demande)
    model["constants"] = constants["convention"]
    model["constants"]["POINT_INDICE"] = constants["point_indice"]
    model["couts_charges"] = constants["recrutement"]["couts_charges"]

    return render_template("calculette_feuille_cout.html", model=model)


@route("/blob/<demande_id>/<blob_id>")
def blob(demande_id: str, blob_id: str, db: SQLAlchemy):
    # current_profile = get_current_profile()
    # demande = db.session.query(Demande).get(id)
    # if not demande:
    #     raise NotFound()
    # # TODO: check access

    filename = "feuille de coût.pdf"

    blob = Blob.query.get(blob_id)
    response = make_response(blob.value)
    response.headers["content-type"] = "application/binary"
    content_disposition = 'attachment;filename="{}"'.format(filename)
    response.headers["content-disposition"] = content_disposition
    return response
