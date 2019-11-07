# from __future__ import annotations
#
# import json
# from typing import Any, Dict, Optional
#
# import structlog
# from abilian.core.util import fqcn
# from flask import current_app, g, jsonify, render_template, request
# from marshmallow.fields import Method
# from marshmallow_sqlalchemy import ModelSchema
# from sqlalchemy.orm import joinedload
#
# from labster.blueprints.util import get_current_user
# from labster.blueprints.v3.demandes.rbac import acces_restreint, \
#     check_read_access
# from labster.domain.models.demandes import Demande
# from labster.domain.models.profiles import Profile
# from labster.domain.services.constants import get_constants
# from labster.newforms import get_form_class_by_name, get_form_class_for
#
# from .. import route
#
# logger = structlog.get_logger()
#
#
# @route("/demandes/<int:id>")
# def demande_view(id):
#     demande = Demande.query.options(
#         joinedload(Demande.structure),
#         joinedload(Demande.contact_dgrtt),
#         joinedload(Demande.gestionnaire),
#         joinedload(Demande.porteur),
#     ).get_or_404(id)
#     check_read_access(demande)
#
#     # breadcrumbs = [{"name": "Demandes", "url": url_for(".demandes")}, {"name": title}]
#
#     constants = get_constants()
#     form = get_form_class_for(demande)()
#
#     ctx = {
#         "demande": demande,
#         "form": form,
#         "acces_restreint": acces_restreint(demande),
#         "constants": constants,
#     }
#     form_data = render_template("demandes/_form_data.html", **ctx)
#
#     try:
#         dto = serialize_demande(demande)
#         dto["form_data"] = form_data
#         return dto
#
#     except Exception as e:
#         msg = f"Error: can not serialize Demande {demande.id}"
#         logger.error(f"{msg}: {e}")
#
#         return (
#             jsonify(
#                 msg=f"La demande {demande.id} comporte des erreurs et ne peut être affichée."
#             ),
#             500,
#         )
#
#
# class DemandeSchema(ModelSchema):
#     class Meta:
#         model = Demande
#
#         include = {
#             "contact_dgrtt": Method("get_contact_dgrtt"),
#             "porteur": Method("get_porteur"),
#             "gestionnaire": Method("get_gestionnaire"),
#         }
#
#     def get_contact_dgrtt(self, obj):
#         return self.get_user_field(obj, "contact_dgrtt")
#
#     def get_porteur(self, obj):
#         return self.get_user_field(obj, "porteur")
#
#     def get_gestionnaire(self, obj):
#         return self.get_user_field(obj, "gestionnaire")
#
#     def get_user_field(self, obj, key):
#         user = getattr(obj, key)
#         return {"full_name": user.full_name, "id": user.id}
#
#         # exclude = ["parents", "children"]
#
#
# def serialize_demande(demande):
#     title = demande.nom
#     form = get_form_class_for(demande)()
#     form.errors = False  # FIXME later
#     current_user = get_current_user()
#     workflow = demande.get_workflow(current_user)
#     # constants = get_constants()
#
#     demande_dto = DemandeSchema().dump(demande).data
#
#     workflow_dto = {
#         "state": {
#             "label": workflow.state.label,
#             "next_action": workflow.state.next_action,
#         }
#     }
#
#     demande_dto["acces_restreint"] = acces_restreint(demande)
#     demande_dto["workflow"] = workflow_dto
#
#     return {"title": title, "demande": demande_dto, "form": form.to_dict()}
#
#
# # @route("/demandes/new")
# # def demande_new() -> Dict:
# #     """Retourne les données nécessaires pour un formulaire vierge."""
# #     type = request.args.get("type", "rh")
# #
# #     labo = get_laboratoire()
# #
# #     # Temp fixes to make crawler work.
# #     if not labo:
# #         return {}
# #         # return "Ignore", 200, {"content-type": "text/plain"}
# #
# #     form_class = get_form_class_by_name(type)
# #
# #     form = form_class(
# #         laboratoire=labo,
# #         porteur=get_porteur(),
# #         gestionnaire=get_gestionnaire(),
# #         mode="create",
# #     )
# #
# #     model = form.model
# #     model["laboratoire"] = labo.nom
# #     porteur = get_porteur()
# #     if porteur and "porteur" in model:
# #         model["porteur"] = porteur.uid
# #
# #     json.dumps(form.to_dict())
# #
# #     return {"form": form.to_dict(), "model": model}
# #
# #     # title = f"Nouvelle demande: {form.label}"
# #     # breadcrumbs = [{"name": "Demandes", "url": url_for(".demandes")}, {"name": title}]
# #
# #     # ctx = {"title": title, "breadcrumbs": breadcrumbs, "model": model, "form": form}
# #
# #     # if form.conditions and not request.args.get("conditions_acceptees"):
# #     #     return render_template("newforms/conditions.html", **ctx)
# #     # else:
# #     #     return render_template("newforms/newform.html", **ctx)
#
#
# # @route("/demandes/<int:id>/form")
# # def demande_edit(id):
# #     demande = Demande.query.get_or_404(id)
# #     if not demande.is_editable_by(g.current_user):
# #         raise MethodNotAllowed()
# #
# #     title = f"Modifier la demande: {demande.nom}"
# #     breadcrumbs = [{"name": "Demandes", "url": url_for(".demandes")}, {"name": title}]
# #
# #     model = demande.data
# #     model["id"] = demande.id
# #     laboratoire = get_laboratoire()
# #     form_class = get_form_class_for(demande)
# #     form = form_class(model=model, laboratoire=laboratoire, mode="edit")
# #
# #     ctx = {"title": title, "breadcrumbs": breadcrumbs, "model": model, "form": form}
# #     return render_template("newforms/newform.html", **ctx)
# #
# #
# # @route("/demandes/post", methods=["POST"])
# # def demande_create_or_edit():
# #     json = request.json
# #     action = json["action"]
# #     model = json["model"]
# #     form = json["form"]
# #     if action == "cancel":
# #         url = demande_cancel_post(model)
# #     elif action == "edit":
# #         url = demande_edit_post(model, form)
# #     elif action == "create":
# #         url = demande_create_post(model, form)
# #     else:
# #         # Should not happen
# #         raise RuntimeError()
# #     return url
# #
# #
# # def demande_cancel_post(model):
# #     if "id" in model:
# #         id = int(model["id"])
# #         demande = Demande.query.get_or_404(id)
# #         return url_for(demande)
# #     else:
# #         return url_for(".demandes")
# #
# #
# # def demande_create_post(model, form):
# #     model = cleanup_model(model, form)
# #
# #     form_type = form["name"]
# #     porteur = get_porteur()
# #
# #     try:
# #         demande = demande_factory(
# #             type=form_type,
# #             demandeur=get_demandeur(),
# #             porteur=porteur,
# #             gestionnaire=get_gestionnaire(),
# #             data=model,
# #         )
# #
# #         demande.form_state = form
# #
# #         db.session.add(demande)
# #         db.session.commit()
# #
# #         flash("Votre demande a été créée.")
# #         if not demande.is_valid():
# #             flash("Attention, votre demande est encore incomplète.", "warning")
# #         return url_for(demande)
# #
# #     except Exception as e:
# #         traceback.print_exc()
# #         flash(
# #             "La demande n'a pas pu être créée (erreur interne). L'administrateur du site a été notifié.",
# #             "warning",
# #         )
# #         logger.error(f"Error on Demande creation of type {form_type}: {e}")
# #         return url_for(".demande_new")
# #
# #
# # def demande_edit_post(model, form):
# #     id = int(model["id"])
# #     demande = Demande.query.get_or_404(id)
# #     if not demande.is_editable_by(g.current_user):
# #         raise MethodNotAllowed()
# #
# #     new_data = model
# #     demande.form_state = form
# #
# #     if not demande.has_same_data(new_data):
# #         demande.update_data(new_data)
# #         db.session.commit()
# #         flash(
# #             "Votre demande a été modifiée. "
# #             "La version précédente de la demande a été archivée."
# #         )
# #     else:
# #         flash("Vous n'avez pas effectué de modification.")
# #
# #     if not demande.is_valid():
# #         flash("Attention, votre demande est encore incomplète.", "warning")
# #     return url_for(demande)
#
#
# #
# # Utility functions
# #
# def get_demandeur() -> Profile:
#     return g.current_user
#
#
# def get_porteur() -> Optional[Profile]:
#     demandeur = get_demandeur()
#     if not demandeur.has_role("gestionnaire"):
#         return demandeur
#     else:
#         return None
#
#
# def get_gestionnaire() -> Optional[Profile]:
#     demandeur = get_demandeur()
#     if demandeur.has_role("gestionnaire"):
#         return demandeur
#     else:
#         return None
#
#
# # FIXME
# def get_laboratoire() -> Any:
#     demandeur = get_demandeur()
#     return demandeur.laboratoire
#
#
# def cleanup_model(model, form):
#     new_model = {}
#     fields = form["fields"]
#     for key, value in model.items():
#         if key not in fields:
#             continue
#         field = fields[key]
#         if not field.get("visible") and value:
#             value = None
#         new_model[key] = value
#
#     return new_model
#
#
# def debug_index(demande: Demande) -> Dict[str, Any]:
#     obj = demande
#     svc = current_app.services["indexing"]
#     index = svc.app_state.indexes["default"]
#     schema = index.schema
#     context = {"schema": schema, "sorted_fields": sorted(schema.names())}
#
#     adapter = svc.adapted.get(fqcn(obj.__class__))
#     if adapter and adapter.indexable:
#         doc = context["current_document"] = svc.get_document(obj, adapter)
#         indexed: Dict[str, Any] = {}
#         for name, field in schema.items():
#             value = doc.get(name)
#             if value and field.analyzer and field.format:
#                 indexed[name] = list(field.process_text(value))
#             else:
#                 indexed[name] = None
#         context["current_indexed"] = indexed
#         context["current_keys"] = sorted(set(doc) | set(indexed))
#
#     with index.searcher() as search:
#         document = search.document(object_key=obj.object_key)
#
#     sorted_keys = sorted(document) if document is not None else None
#
#     context.update({"document": document, "sorted_keys": sorted_keys})
#
#     return context
from __future__ import annotations
