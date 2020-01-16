from __future__ import annotations

import structlog
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from marshmallow.fields import Method
from marshmallow_sqlalchemy import TableSchema
from more_itertools import first
from sqlalchemy.orm import joinedload

from labster.di import injector
from labster.domain2.model.demande import Demande
from labster.domain2.services.roles import Role, RoleService
from labster.infrastructure.repositories.sqla.mappers import Mapper
from labster.newforms import get_form_class_by_name, get_form_class_for
from labster.rbac import acces_restreint, feuille_cout_editable
from labster.rpc.registry import context_for
from labster.security import get_current_profile
from labster.types import JSON, JSONDict

logger = structlog.get_logger()
mapper = injector.get(Mapper)
db = injector.get(SQLAlchemy)


@context_for("demande.new")
def get_new(type: str = "rh") -> JSONDict:
    """Retourne les données nécessaires pour un formulaire vierge."""
    form_class = get_form_class_by_name(type)
    form = form_class(mode="create")
    model = form.empty_model()
    post_process_form_and_model(form, model)
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
    # FIXME!!!!
    # check_read_access(demande)

    # constants = get_constants()

    form = get_form_class_for(demande)()
    form.errors = False  # FIXME later
    post_process_form_and_model(form)

    demande_dto = DemandeSchema().dump(demande).data

    return {"demande": demande_dto, "form": form.to_dict()}


def post_process_form_and_model(form, model=None):
    user = get_current_profile()
    role_service = injector.get(RoleService)
    roles = role_service.get_roles_for_user(user)
    structures_d_affectation = roles[Role.MEMBRE_AFFECTE]

    # Cas "Porteur"
    field = form.get_field("laboratoire")
    field.choices = [[s.id, s.nom] for s in structures_d_affectation]

    field = form.get_field("porteur")
    choices = [[user.id, user.full_name]]
    field.choices = choices

    if not model:
        return

    porteur = user
    model["porteur"] = porteur.id

    model["laboratoire"] = first(structures_d_affectation).id


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
