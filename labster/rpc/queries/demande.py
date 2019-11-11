from __future__ import annotations

import json
from typing import Any, Dict, Optional

import structlog
from abilian.core.util import fqcn
from flask import current_app, g
from jsonrpcserver import method
from marshmallow.fields import Method
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy.orm import joinedload

from labster.domain.models.demandes import Demande
from labster.domain.models.profiles import Profile
from labster.domain.models.unites import OrgUnit
from labster.newforms import get_form_class_by_name, get_form_class_for
from labster.rbac import acces_restreint, check_read_access
from labster.rpc.registry import context_for
from labster.types import JSON, JSONDict
from labster.util import get_current_user

logger = structlog.get_logger()


@context_for("demande.new")
def get_new(type: str = "rh") -> JSONDict:
    """Retourne les données nécessaires pour un formulaire vierge."""
    labo = get_laboratoire()

    # Temp fixes to make crawler work.
    if not labo:
        return {}
        # return "Ignore", 200, {"content-type": "text/plain"}

    form_class = get_form_class_by_name(type)

    form = form_class(
        laboratoire=labo,
        porteur=get_porteur(),
        gestionnaire=get_gestionnaire(),
        mode="create",
    )

    model = form.empty_model()
    model["laboratoire"] = labo.nom

    porteur = get_porteur()
    if porteur and "porteur" in model:
        model["porteur"] = porteur.uid

    json.dumps(form.to_dict())

    return {"form": form.to_dict(), "model": model}


@method
def get_demande(id: str) -> JSON:
    demande = Demande.query.options(
        joinedload(Demande.structure),
        joinedload(Demande.contact_dgrtt),
        joinedload(Demande.gestionnaire),
        joinedload(Demande.porteur),
    ).get_or_404(id)
    check_read_access(demande)

    # constants = get_constants()

    form = get_form_class_for(demande)()
    form.errors = False  # FIXME later

    demande_dto = DemandeSchema().dump(demande).data

    return {"demande": demande_dto, "form": form.to_dict()}

    # try:
    #     dto = serialize_demande(demande)
    #     dto["form_data"] = form_data
    #     return dto
    #
    # except Exception as e:
    #     msg = f"Error: can not serialize Demande {demande.id}"
    #     logger.error(f"{msg}: {e}")
    #
    #     return (
    #         jsonify(
    #             msg=f"La demande {demande.id} comporte des erreurs et ne peut être affichée."
    #         ),
    #         500,
    #     )


#
# Serialization
#
class DemandeSchema(ModelSchema):
    class Meta:
        model = Demande

        include = {
            "contact_dgrtt": Method("get_contact_dgrtt"),
            "porteur": Method("get_porteur"),
            "gestionnaire": Method("get_gestionnaire"),
            "form_data": Method("get_form_data"),
            "workflow": Method("get_workflow"),
            "acces_restreint": Method("get_acces_restreint"),
        }

    def get_contact_dgrtt(self, obj: Demande):
        return self.get_user_field(obj, "contact_dgrtt")

    def get_porteur(self, obj: Demande):
        return self.get_user_field(obj, "porteur")

    def get_gestionnaire(self, obj: Demande):
        return self.get_user_field(obj, "gestionnaire")

    def get_user_field(self, obj: Demande, key):
        user = getattr(obj, key)
        return {"full_name": user.full_name, "id": user.id}

    def get_form_data(self, obj: Demande):
        return dict(obj.data)

    def get_workflow(self, obj: Demande) -> JSON:
        current_user = get_current_user()
        workflow = obj.get_workflow(current_user)
        return {
            "state": {
                "label": workflow.state.label,
                "next_action": workflow.state.next_action,
            }
        }

    def get_acces_restreint(self, obj: Demande) -> bool:
        return acces_restreint(obj)

        # exclude = ["parents", "children"]


#
# Utility functions
#
def get_demandeur() -> Profile:
    return g.current_user


def get_porteur() -> Optional[Profile]:
    demandeur = get_demandeur()
    if not demandeur.has_role("gestionnaire"):
        return demandeur
    else:
        return None


def get_gestionnaire() -> Optional[Profile]:
    demandeur = get_demandeur()
    if demandeur.has_role("gestionnaire"):
        return demandeur
    else:
        return None


# FIXME
def get_laboratoire() -> Optional[OrgUnit]:
    demandeur = get_demandeur()
    return demandeur.laboratoire


def cleanup_model(model, form):
    new_model = {}
    fields = form["fields"]
    for key, value in model.items():
        if key not in fields:
            continue
        field = fields[key]
        if not field.get("visible") and value:
            value = None
        new_model[key] = value

    return new_model


def debug_index(demande: Demande) -> JSONDict:
    obj = demande
    svc = current_app.services["indexing"]
    index = svc.app_state.indexes["default"]
    schema = index.schema
    context = {"schema": schema, "sorted_fields": sorted(schema.names())}

    adapter = svc.adapted.get(fqcn(obj.__class__))
    if adapter and adapter.indexable:
        doc = context["current_document"] = svc.get_document(obj, adapter)
        indexed: Dict[str, Any] = {}
        for name, field in schema.items():
            value = doc.get(name)
            if value and field.analyzer and field.format:
                indexed[name] = list(field.process_text(value))
            else:
                indexed[name] = None
        context["current_indexed"] = indexed
        context["current_keys"] = sorted(set(doc) | set(indexed))

    with index.searcher() as search:
        document = search.document(object_key=obj.object_key)

    sorted_keys = sorted(document) if document is not None else None

    context.update({"document": document, "sorted_keys": sorted_keys})

    return context
