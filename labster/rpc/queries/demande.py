from __future__ import annotations

from typing import Optional

import structlog
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from marshmallow.fields import Method
from marshmallow_sqlalchemy import TableSchema
from sqlalchemy.orm import joinedload

from labster.di import injector
from labster.domain2.model.demande import Demande
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.domain2.services.constants import get_constants
from labster.infrastructure.repositories.sqla.mappers import Mapper
from labster.newforms import get_form_class_by_name, get_form_class_for
from labster.rbac import acces_restreint, check_read_access, \
    feuille_cout_editable
from labster.rpc.registry import context_for
from labster.security import get_current_profile
from labster.types import JSON, JSONDict

logger = structlog.get_logger()
mapper = injector.get(Mapper)
db = injector.get(SQLAlchemy)


@context_for("demande.new")
def get_new(type: str = "rh") -> JSONDict:
    """Retourne les données nécessaires pour un formulaire vierge."""
    structure = get_structure()

    form_class = get_form_class_by_name(type)

    form = form_class(
        laboratoire=structure,
        porteur=get_porteur(),
        gestionnaire=get_gestionnaire(),
        mode="create",
    )

    model = form.empty_model()
    if structure and "laboratoire" in model:
        model["laboratoire"] = structure.nom

    porteur = get_porteur()
    if porteur and "porteur" in model:
        model["porteur"] = porteur.uid

    return {"form": form.to_dict(), "model": model}


@method
def get_demande(id: str) -> JSON:
    demande = (
        db.session.query(Demande)
        .options(
            joinedload(Demande.structure),
            joinedload(Demande.contact_labco),
            joinedload(Demande.gestionnaire),
            joinedload(Demande.porteur),
        )
        .get(id)
    )
    check_read_access(demande)

    # constants = get_constants()

    form = get_form_class_for(demande)()
    form.errors = False  # FIXME later

    demande_dto = DemandeSchema().dump(demande).data

    # for k in DemandeSchema.Meta.include:
    #     pprint([k, demande_dto.get(k, "????")])
    #     sys.stdout.flush()

    return {"demande": demande_dto, "form": form.to_dict()}


#
# Serialization
#
class DemandeSchema(TableSchema):
    class Meta:
        # model = Demande
        table = mapper.metadata.tables["v3_demandes"]

        include = {
            # Permissions
            "acces_restreint": Method("get_acces_restreint"),
            "is_editable": Method("get_is_editable"),
            "is_duplicable": Method("get_is_duplicable"),
            "feuille_cout_editable": Method("get_feuille_cout_editable"),
            # Key users
            "contact_labco": Method("get_contact_labco"),
            "porteur": Method("get_porteur"),
            "gestionnaire": Method("get_gestionnaire"),
            # Form
            "form_data": Method("get_form_data"),
            # For tabs
            "pieces_jointes": Method("get_pieces_jointes"),
            "workflow": Method("get_workflow"),
            "workflow_history": Method("get_history"),
            "past_versions": Method("get_past_versions"),
            "is_valid": Method("get_is_valid"),
        }

    # Permissions
    def get_acces_restreint(self, obj: Demande) -> bool:
        return acces_restreint(obj)

    def get_is_editable(self, obj: Demande) -> bool:
        return obj.is_editable_by(get_current_profile())

    def get_is_duplicable(self, obj: Demande) -> bool:
        return obj.is_duplicable_by(get_current_profile())

    def get_feuille_cout_editable(self, obj: Demande) -> bool:
        return feuille_cout_editable(obj)

    # Serialize key users
    def get_contact_labco(self, obj: Demande):
        return self.get_user_field(obj, "contact_labco")

    def get_porteur(self, obj: Demande):
        return self.get_user_field(obj, "porteur")

    def get_gestionnaire(self, obj: Demande):
        return self.get_user_field(obj, "gestionnaire")

    def get_user_field(self, obj: Demande, key):
        user = getattr(obj, key)
        return {"full_name": user.full_name, "id": user.id}

    # Form
    def get_form_data(self, obj: Demande):
        return dict(obj.data)

    # Tabs
    def get_workflow(self, obj: Demande) -> JSON:
        current_user = get_current_profile()
        workflow = obj.get_workflow(current_user)
        owners = [
            {"full_name": owner.full_name, "id": owner.id}
            for owner in workflow.current_owners()
        ]
        transitions = [
            {"id": t.id, "label": t.label, "category": t.category}
            for t in workflow.possible_transitions()
        ]

        result = {
            "state": {
                "label": workflow.state.label,
                "next_action": workflow.state.next_action,
            },
            "owners": owners,
            "history": [],  # TODO
            "transitions": transitions,
        }
        return result

    # Pour l'onglet "Pièces à joindre"
    def get_pieces_jointes(self, obj: Demande) -> JSON:
        return obj.pieces_jointes

    # Pour l'onglet "Documents générés"
    def get_is_valid(self, obj: Demande) -> JSON:
        return obj.is_valid()

    # Pour l'onglet "historique"
    def get_past_versions(self, obj: Demande) -> JSON:
        return obj.past_versions

    def get_history(self, obj: Demande) -> JSON:
        return obj.wf_history

    # Workflow
    def get_possible_transitions(self, obj: Demande) -> JSON:
        user = get_current_profile()
        return obj.get_workflow(user).possible_transitions()


#
# Utility functions
#
def get_demandeur() -> Profile:
    return get_current_profile()


def get_porteur() -> Optional[Profile]:
    return None
    # FIXME
    # demandeur = get_demandeur()
    # if not demandeur.has_role("gestionnaire"):
    #     return demandeur
    # else:
    #     return None


def get_gestionnaire() -> Optional[Profile]:
    return None
    # FIXME
    # demandeur = get_demandeur()
    # if demandeur.has_role("gestionnaire"):
    #     return demandeur
    # else:
    #     return None


# FIXME
def get_structure() -> Optional[Structure]:
    return None
    # FIXME
    # demandeur = get_demandeur()
    # return demandeur.laboratoire


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
