from __future__ import annotations

from datetime import datetime

from abilian.core.models.blob import Blob
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from weasyprint import HTML
from werkzeug.exceptions import Forbidden, MethodNotAllowed, NotFound

from labster.di import injector
from labster.domain2.model.demande import Demande, demande_factory
from labster.domain2.model.profile import Profile
from labster.security import get_current_profile

db = injector.get(SQLAlchemy)


@method
def create_demande(model, form):
    user = get_current_profile()
    # TODO
    # ensure_role("alc")

    model = cleanup_model(model, form)

    form_type = form["name"]

    porteur_id = model.get("porteur")
    if porteur_id:
        porteur = db.session.query(Profile).get(porteur_id)
    else:
        porteur = None

    if user != porteur:
        gestionnaire = user
    else:
        gestionnaire = None

    # porteur = get_porteur()

    demande = demande_factory(type=form_type, demandeur=user, data=model,)
    demande.porteur = porteur
    demande.gestionnaire = gestionnaire

    demande.form_state = form

    db.session.add(demande)
    db.session.commit()

    messages = [
        ["Votre demande a été créée.", "success"],
    ]
    if not demande.is_valid():
        messages.append(["Attention, votre demande est encore incomplète.", "warning"])

    return {
        "id": demande.id,
        "messages": messages,
    }


@method
def update_demande(id, model, form):
    model = cleanup_model(model, form)

    user = get_current_profile()

    # TODO: replace
    demande = db.session.query(Demande).get(id)
    assert demande
    if not demande.is_editable_by(user):
        raise MethodNotAllowed()

    new_data = model
    demande.form_state = form

    messages = []
    if not demande.has_same_data(new_data):
        demande.update_data(new_data)
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

    return messages


@method
def update_feuille_de_cout(model, html):
    current_profile = get_current_profile()
    id = model["id"]
    demande = db.session.query(Demande).get(id)

    if not demande:
        raise NotFound()

    # _check_read_access(demande)  # TODO: check write access
    if not demande.is_editable_by(current_profile):
        raise Forbidden()

    demande.feuille_cout = model
    db.session.commit()

    s = HTML(string=html).write_pdf()
    assert s

    blob = Blob(s)
    db.session.add(blob)
    db.session.flush()
    d = {
        "name": "Feuille de coût",
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

    # return url_for(demande)
    #
    #
    # form_type = form["name"]
    # porteur = get_porteur()
    #
    # demande = demande_factory(
    #     type=form_type,
    #     demandeur=get_demandeur(),
    #     porteur=porteur,
    #     gestionnaire=get_gestionnaire(),
    #     data=model,
    # )
    #
    # demande.form_state = form
    #
    # db.session.add(demande)
    # db.session.commit()
    #
    # return demande.id
    #
    # # flash("Votre demande a été créée.")
    # # if not demande.is_valid():
    # #     flash("Attention, votre demande est encore incomplète.", "warning")
    # # return url_for(demande)


# def demande_edit_post(model, form):


# @route("/demandes/post", methods=["POST"])
# def demande_create_or_edit():
#     json = request.json
#     action = json["action"]
#     model = json["model"]
#     form = json["form"]
#     if action == "cancel":
#         url = demande_cancel_post(model)
#     elif action == "edit":
#         url = demande_edit_post(model, form)
#     elif action == "create":
#         url = demande_create_post(model, form)
#     else:
#         # Should not happen
#         raise RuntimeError()
#     return url
#
#
# def demande_create_post(model, form):
#     model = cleanup_model(model, form)
#
#     form_type = form["name"]
#     porteur = get_porteur()
#
#     try:
#         demande = demande_factory(
#             type=form_type,
#             demandeur=get_demandeur(),
#             porteur=porteur,
#             gestionnaire=get_gestionnaire(),
#             data=model,
#         )
#
#         demande.form_state = form
#
#         db.session.add(demande)
#         db.session.commit()
#
#         flash("Votre demande a été créée.")
#         if not demande.is_valid():
#             flash("Attention, votre demande est encore incomplète.", "warning")
#         return url_for(demande)
#
#     except Exception as e:
#         traceback.print_exc()
#         flash(
#             "La demande n'a pas pu être créée (erreur interne). L'administrateur du site a été notifié.",
#             "warning",
#         )
#         logger.error(f"Error on Demande creation of type {form_type}: {e}")
#         return url_for(".demande_new")
