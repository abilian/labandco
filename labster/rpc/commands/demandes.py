from __future__ import annotations

from typing import Dict

from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from marshmallow import pprint

from labster.di import injector
from labster.domain.models.demandes import demande_factory
from labster.rpc.queries.demande import cleanup_model, get_demandeur, \
    get_gestionnaire, get_porteur

from ..util import ensure_role

db = injector.get(SQLAlchemy)


@method
def create_demande(model, form):
    # TODO
    # ensure_role("alc")

    pprint(model)
    pprint(form)

    model = cleanup_model(model, form)

    form_type = form["name"]
    porteur = get_porteur()

    demande = demande_factory(
        type=form_type,
        demandeur=get_demandeur(),
        porteur=porteur,
        gestionnaire=get_gestionnaire(),
        data=model,
    )

    demande.form_state = form

    db.session.add(demande)
    db.session.commit()

    return demande.id

    # flash("Votre demande a été créée.")
    # if not demande.is_valid():
    #     flash("Attention, votre demande est encore incomplète.", "warning")
    # return url_for(demande)


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
