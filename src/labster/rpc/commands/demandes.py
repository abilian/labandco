from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from abilian.core.models.blob import Blob
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from sqlalchemy import func
from toolz import first
from weasyprint import CSS, HTML
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from labster.di import injector
from labster.domain2.model.demande import Demande, demande_factory
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure, StructureRepository
from labster.extensions import whoosh
from labster.rbac import check_can_add_pj, check_read_access, \
    check_write_access, feuille_cout_editable
from labster.security import get_current_profile

db = injector.get(SQLAlchemy)
structure_repo = injector.get(StructureRepository)


PRINT_CSS = """
.print .feuille-cout {
    input {
        display: none;
    }

    select {
        display: none;
    }

    .no-print {
        display: none;
    }

    .only-print {
        display: inline;
    }
}

.only-print {
    display: none;
}
"""


@method
def create_demande(model, form):
    user = get_current_profile()
    # TODO: check permissions

    model = cleanup_model(model, form)

    form_type = form["name"]

    demande = demande_factory(type=form_type, demandeur=user, data=model)

    demande.porteur = get_porteur(model)
    demande.structure = get_structure(model)

    if user != demande.porteur:
        demande.gestionnaire = user
    else:
        demande.gestionnaire = None

    demande.form_state = form

    new_id = db.session.query(func.max(Demande.id)).one()[0] + 1
    demande.id = new_id

    db.session.add(demande)
    db.session.commit()

    messages = [
        ["Votre demande a été créée.", "success"],
    ]
    if not demande.is_valid():
        messages.append(["Attention, votre demande est encore incomplète.", "warning"])

    whoosh.index_object(demande)

    return {
        "id": demande.id,
        "messages": messages,
    }


@method
def update_demande(id, model, form):
    user = get_current_profile()
    model = cleanup_model(model, form)

    demande = db.session.query(Demande).get(id)
    check_read_access(demande)
    check_write_access(demande)

    demande.form_state = form

    messages = []
    if not demande.has_same_data(model):
        demande.update_data(model)
        porteur = get_porteur(model)
        if porteur != demande.porteur:
            demande.porteur = porteur
            demande.gestionnaire = user
        demande.structure = get_structure(model)
        db.session.commit()

        messages.append(
            [
                "Votre demande a été modifiée. La version précédente de la demande a été archivée.",
                "success",
            ]
        )
    else:
        messages.append(["Vous n'avez pas effectué de modification.", "success"])

    if not demande.is_valid():
        messages.append(["Attention, votre demande est encore incomplète.", "warning"])

    whoosh.index_object(demande)

    return messages


def get_structure(model: dict) -> Structure | None:
    structure_dto = model.get("laboratoire")
    if not structure_dto:
        return None

    if isinstance(structure_dto, str):
        structure_id = structure_dto
    elif isinstance(structure_dto, dict):
        structure_id = structure_dto["value"]
    else:
        raise BadRequest

    structure = structure_repo.get_by_id(structure_id)
    return structure


def get_porteur(model: dict) -> Profile | None:
    porteur_dto = model.get("porteur")
    if not porteur_dto:
        return None

    if isinstance(porteur_dto, str):
        porteur_id = porteur_dto
    elif isinstance(porteur_dto, dict):
        porteur_id = porteur_dto["value"]
    else:
        raise BadRequest
    porteur = db.session.query(Profile).get(porteur_id)
    return porteur


@method
def dupliquer_demande(id):
    demande = db.session.query(Demande).get(id)
    check_read_access(demande)

    new_id = db.session.query(func.max(Demande.id)).one()[0] + 1
    nouvelle_demande = demande.clone()
    nouvelle_demande.id = new_id

    db.session.add(nouvelle_demande)
    db.session.commit()

    return nouvelle_demande.id


@method
def delete_pj(demande_id, blob_id):
    demande: Demande = db.session.query(Demande).get(demande_id)
    check_can_add_pj(demande)

    attachments = demande.attachments.copy()
    filename = None
    for filename, v in demande.attachments.items():
        if v["id"] == blob_id:
            filename = filename
            break
    if filename:
        del attachments[filename]
    demande.attachments = attachments
    db.session.commit()


@method
def update_feuille_de_cout(model, html):
    id = model["id"]
    demande = db.session.query(Demande).get(id)

    if not demande:
        raise NotFound()

    if not feuille_cout_editable(demande):
        raise Forbidden()

    demande.feuille_cout = model
    html = re.sub('id="feuille-cout"', 'id="feuille-cout" class="print"', html)
    demande.data["fdc_html"] = f'<!DOCTYPE html><html lang="fr-FR">{html}</html>'
    db.session.commit()

    root = Path(current_app.root_path)
    static = root / "static"
    css = static / "css"

    css1 = CSS(filename=str(first(css.glob("chunk*"))))
    css2 = CSS(filename=str(first(css.glob("app*"))))
    css3 = CSS(string=PRINT_CSS)

    s = HTML(string=html).write_pdf(stylesheets=[css3, css1, css2, css3])
    assert s

    blob = Blob(s)
    db.session.add(blob)
    db.session.flush()

    d = {
        "name": "Feuille de coût.pdf",
        "date": datetime.utcnow().isoformat(),
        "blob_id": blob.id,
    }
    if demande.documents_generes:
        docs = list(demande.documents_generes)
        docs.append(d)
        demande.documents_generes = docs
    else:
        demande.documents_generes = [d]
    db.session.commit()


def make_pdf(model):
    pass


#
# Utility functions
#
def cleanup_model(model, form):
    """Remove values for fields that are not visible."""
    new_model = {}
    fields = form["fields"]
    for key, value in model.items():
        if key not in fields:
            continue
        if key.startswith("html-"):
            continue
        field = fields[key]
        if not field.get("visible") and value:
            value = None
        new_model[key] = value

    return new_model
