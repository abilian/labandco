"""Main blueprint."""
from __future__ import annotations

import mimetypes
from datetime import datetime

import magic
from abilian.core.models.blob import Blob
from flask import Blueprint, Request, make_response, redirect, \
    render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import Forbidden, NotFound

from labster.domain2.model.demande import Demande, DemandeRH
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.constants import get_constants
from labster.domain2.services.documents_generes import devis_rh, \
    lettre_commande_rh
from labster.rbac import acces_restreint, check_can_add_pj, \
    check_read_access, feuille_cout_editable
from labster.rpc.commands.demandes import cleanup_model
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
def feuille_cout(id: int, db: SQLAlchemy):
    constants = get_constants()

    demande = db.session.query(Demande).get(id)
    check_read_access(demande)

    model = demande.feuille_cout or {}
    model["id"] = demande.id
    model["editable"] = feuille_cout_editable(demande)
    model["constants"] = constants["convention"]
    model["constants"]["POINT_INDICE"] = constants["point_indice"]
    model["couts_charges"] = constants["recrutement"]["couts_charges"]

    return render_template("calculette_feuille_cout.html", model=model)


@route("/blob/<int:demande_id>/<int:blob_id>")
def blob(demande_id: int, blob_id: int, db: SQLAlchemy):
    demande = db.session.query(Demande).get(demande_id)
    blob = Blob.query.get(blob_id)
    if not demande or not blob:
        raise NotFound()

    check_read_access(demande)

    def get_filename(demande, blob_id):
        for filename, v in demande.attachments.items():
            if v["id"] == blob_id:
                return filename

        for d in demande.documents_generes:
            if d["blob_id"] == blob_id:
                return d["name"]

        return "fichier inconnu"

    filename = get_filename(demande, blob_id)
    suffix = get_suffix_for(blob.value or b"")
    if not suffix:
        suffix = ".pdf"
    if not filename.endswith(suffix):
        filename = filename + suffix

    response = make_response(blob.value or "")
    if blob.value:
        response.headers["content-type"] = magic.from_buffer(blob.value, mime=True)
    else:
        response.headers["content-type"] = "text/plain"
    content_disposition = f'attachment;filename="{filename}"'
    response.headers["content-disposition"] = content_disposition.encode()
    return response


def get_suffix_for(value: bytes):
    mime_type = magic.from_buffer(value, mime=True)
    extension = mimetypes.guess_extension(mime_type)
    return extension


@route("/upload/", methods=["POST"])
def upload(request: Request, db: SQLAlchemy):
    user = get_current_profile()
    form = request.form
    demande_id = form["demande_id"]
    demande = db.session.query(Demande).get(demande_id)
    check_can_add_pj(demande)

    files = request.files
    for file in files.values():
        file_name = file.filename

        data = file.read()
        blob = Blob(data)
        db.session.add(blob)
        db.session.flush()

        demande.attachments[file_name] = {
            "date": datetime.now().isoformat(),
            "id": blob.id,
            "creator": user.login,
        }

    db.session.commit()
    return "OK"


@route("/demandes/<int:id>/devis_rh")
def devis_rh_rest(id, db: SQLAlchemy):
    demande = db.session.query(Demande).get(id)
    if acces_restreint(demande):
        raise Forbidden()

    assert isinstance(demande, DemandeRH)

    response = make_response(devis_rh(demande))
    response.headers["content-type"] = "application/pdf"
    content_disposition = 'attachment;filename="devis-rh.pdf"'
    response.headers["content-disposition"] = content_disposition.encode()
    return response


@route("/calculettes/devis_rh", methods=["POST"])
def calculette_rh(db: SQLAlchemy, structure_repo: StructureRepository):
    demande = DemandeRH()

    json = request.json

    model = json["model"]
    form = json["form"]

    user = get_current_profile()

    model = cleanup_model(model, form)

    demande = DemandeRH(data=model)
    demande.form_state = form

    porteur_dto = model.get("porteur")
    if porteur_dto:
        porteur_id = porteur_dto["value"]
        demande.porteur = db.session.query(Profile).get(porteur_id)

    if user != demande.porteur:
        demande.gestionnaire = user

    structure_dto = model.get("laboratoire")
    if structure_dto:
        structure_id = structure_dto["value"]
        demande.structure = structure_repo.get_by_id(structure_id)

    blob = devis_rh(demande)
    response = make_response(blob)
    response.headers["content-type"] = "application/pdf"
    return response


@route("/demandes/<int:id>/lettre_commande_rh")
def lettre_commande_rh_rest(id, db: SQLAlchemy):
    demande = db.session.query(Demande).get(id)
    if acces_restreint(demande):
        raise Forbidden()

    assert isinstance(demande, DemandeRH)

    response = make_response(lettre_commande_rh(demande))
    response.headers["content-type"] = "application/pdf"
    content_disposition = 'attachment;filename="lettre-commande-rh.pdf"'
    response.headers["content-disposition"] = content_disposition.encode()
    return response


@route("/demandes/<int:id>/fdc")
def fdc(id: int, db: SQLAlchemy):
    demande = db.session.query(Demande).get(id)

    # model = demande.feuille_cout
    html = demande.data["fdc_html"].encode("utf8")

    return html, 200, {"content-type": "text/html"}

    # css = CSS(string="")
    #
    # s = HTML(string=html).write_pdf(stylesheets=[css])
    # assert s
    # return html, 200, {"content-type": "application/pdf"}

    # response = make_response(s)
    # response.headers["content-type"] = "application/pdf"
    # return response


@route("/demandes_a_valider/<type>")
@route("/demandes_a_valider/")
def demandes_a_valider(type=None):
    if type:
        return redirect(f"/#/demandes_a_valider/{type}")
    else:
        return redirect("/#/tasks")
