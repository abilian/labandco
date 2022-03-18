from __future__ import annotations

from functools import singledispatch
from typing import Any

import structlog
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from marshmallow.fields import Method
from marshmallow_sqlalchemy import TableSchema
from more_itertools import first

from labster.di import injector
from labster.domain2.model.demande import Demande, DemandeRH
from labster.domain2.model.profile import Profile
from labster.domain2.services.roles import Role, RoleService
from labster.infrastructure.repositories.sqla.mappers import Mapper
from labster.newforms import get_form_class_by_name, get_form_class_for
from labster.rbac import acces_restreint, can_duplicate, check_read_access, \
    feuille_cout_editable, has_write_access
from labster.rpc.registry import context_for
from labster.rpc.util import owner_sorter
from labster.security import get_current_profile
from labster.types import JSON, JSONDict, JSONList

logger = structlog.get_logger()
mapper = injector.get(Mapper)
db = injector.get(SQLAlchemy)
role_service = injector.get(RoleService)


@context_for("demande.new")
@method
def get_new(type: str = "calculette_rh") -> JSONDict:
    """Retourne les données nécessaires pour un formulaire vierge."""
    calculette = False
    if type == "calculette_rh":
        calculette = True
        type = "rh"
    form_class = get_form_class_by_name(type)
    form = form_class(mode="create")
    form.update_choices()

    if calculette:
        hide_fields(form)

    model = form.empty_model()
    post_process_form_and_model(form, model)
    return {"form": form.to_dict(), "model": model}


@method
def get_demande(id: str) -> JSON:
    demande = db.session.query(Demande).get(id)
    check_read_access(demande)

    form = get_form_class_for(demande)()
    form.errors = False  # FIXME later
    post_process_form_and_model(form)

    demande_dto = DemandeSchema().dump(demande).data
    demande_dto = add_more_fields(demande, demande_dto)

    if demande_dto["is_editable"]:
        form.update_choices()

    return {"demande": demande_dto, "form": form.to_dict()}


#
# Util
#
def post_process_form_and_model(form, model=None):
    user = get_current_profile()
    roles = role_service.get_roles_for_user(user)
    structures_d_affectation = roles[Role.MEMBRE_AFFECTE]

    structures_comme_gestionnaire = roles[Role.GESTIONNAIRE]
    structures_comme_porteur = roles[Role.PORTEUR]

    structures = []
    if structures_comme_gestionnaire:
        structures += structures_comme_gestionnaire
    if structures_comme_porteur:
        structures += structures_comme_porteur

    field = form.get_field("laboratoire")
    field.choices = [{"value": s.id, "label": s.nom} for s in structures]

    porteurs = {user}
    for structure in structures_comme_gestionnaire:
        membres = role_service.get_users_with_given_role(Role.PORTEUR, structure)
        porteurs.update(membres)

    field = form.get_field("porteur")
    choices = [
        {"value": user.id, "label": f"{user.nom}, {user.prenom}"}
        for user in sorted(porteurs, key=lambda x: (x.nom, x.prenom))
    ]
    field.choices = choices

    if not model:
        return

    porteur = user
    model["porteur"] = {"value": porteur.id, "label": f"{user.nom}, {user.prenom}"}

    structure = first(structures_d_affectation)
    model["laboratoire"] = {"value": structure.id, "label": structure.nom}


#
# Helper for calculette
#
def hide_fields(form):
    fieldsets = form.fieldsets
    get_fieldset(fieldsets, "laboratoire").hidden = True
    get_fieldset(fieldsets, "responsable_scientifique").hidden = True
    get_fieldset(fieldsets, "contrat").hidden = True
    get_fieldset(fieldsets, "structures_concernees").hidden = True

    # Afficher "experience professionnelle", pour montrer le salaire indicatif.
    # fieldsets 4, 5: experience professionnelle.
    get_fieldset(fieldsets, "candidat").hidden = False  # but show just two fieldsets
    get_fieldset(fieldsets, "candidat").fields[0].hidden = True
    get_fieldset(fieldsets, "candidat").fields[1].hidden = True
    get_fieldset(fieldsets, "candidat").fields[2].hidden = True
    get_fieldset(fieldsets, "candidat").fields[3].hidden = True

    get_fieldset(fieldsets, "autre_modification").hidden = True
    get_fieldset(fieldsets, "publicite").hidden = True
    get_fieldset(fieldsets, "commentaire").hidden = True

    get_fieldset(fieldsets, "poste").fields[0].hidden = True
    get_fieldset(fieldsets, "poste").fields[1].hidden = True
    # equivalent corps/grade
    get_fieldset(fieldsets, "poste").fields[2].hidden = False
    get_fieldset(fieldsets, "poste").fields[3].hidden = True


def get_fieldset(fieldsets, name):
    """Return a fieldset."""
    for it in fieldsets:
        if it.name == name:
            return it

    raise RuntimeError(
        f"Could not find fieldset {name}. This is not supposed to happen."
    )


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
            "contributeurs": Method("get_contributeurs"),
            # Structure
            "structure": Method("get_structure"),
            # Form
            "form_data": Method("get_form_data"),
            # For tabs
            "pieces_jointes": Method("get_pieces_jointes"),
            "workflow": Method("get_workflow"),
            "workflow_history": Method("get_history"),
            "past_versions": Method("get_past_versions"),
            "is_valid": Method("get_is_valid"),
            "errors": Method("get_errors"),
            "extra_errors": Method("get_extra_errors"),
        }

    # Permissions
    def get_acces_restreint(self, demande: Demande) -> bool:
        return acces_restreint(demande)

    def get_is_editable(self, demande: Demande) -> bool:
        return has_write_access(demande)

    def get_is_duplicable(self, demande: Demande) -> bool:
        return can_duplicate(demande)

    def get_feuille_cout_editable(self, demande: Demande) -> bool:
        return feuille_cout_editable(demande)

    # Serialize key users
    def get_contact_labco(self, demande: Demande):
        return self.get_user_field(demande, "contact_labco")

    def get_porteur(self, demande: Demande):
        return self.get_user_field(demande, "porteur")

    def get_gestionnaire(self, demande: Demande):
        return self.get_user_field(demande, "gestionnaire")

    def get_user_field(self, demande: Demande, key):
        user = getattr(demande, key)
        return {"full_name": user.full_name, "id": user.id}

    def get_contributeurs(self, demande: Demande):
        contributeur_ids = {x["value"] for x in demande.data.get("contributeurs", [])}
        contributeurs = set()
        for id in contributeur_ids:
            contributeur = db.session.query(Profile).get(id)
            if contributeur and contributeur.active:
                contributeurs.add(contributeur)
        return [{"full_name": p.full_name, "id": p.id} for p in contributeurs]

    def get_structure(self, demande: Demande):
        structure = demande.structure
        if structure:
            return {"id": structure.id, "label": structure.nom}
        else:
            return {}

    # Form
    def get_form_data(self, demande: Demande):
        return dict(demande.data)

    def get_errors(self, demande: Demande):
        return demande.errors

    def get_extra_errors(self, demande: Demande):
        return demande.get_extra_errors()

    # Tabs
    def get_workflow(self, demande: Demande) -> JSON:
        current_user = get_current_profile()
        workflow = demande.get_workflow(current_user)

        owners = list(workflow.current_owners())

        owners.sort(key=owner_sorter)
        owners_dto = [
            {"full_name": owner.full_name, "id": owner.id} for owner in owners
        ]

        transitions_dto = [
            {
                "id": t.id,
                "label": t.label,
                "category": t.category,
                "form": t.get_form(workflow),
            }
            for t in workflow.possible_transitions()
        ]

        result = {
            "state": {
                "label": workflow.state.label,
                "next_action": workflow.state.next_action,
            },
            "owners": owners_dto,
            "history": [],  # TODO
            "transitions": transitions_dto,
        }
        return result

    # Pour l'onglet "Pièces à joindre"
    def get_pieces_jointes(self, obj: Demande) -> JSONList:
        result: list[dict[str, Any]] = []
        for name, v in obj.attachments.items():
            creator_login = v["creator"]
            creator = (
                db.session.query(Profile).filter(Profile.login == creator_login).first()
            )
            if creator:
                creator_dto = {"id": creator.id, "name": creator.full_name}
            else:
                creator_dto = {"id": None, "name": "Utilisateur inconnu"}

            result.append(
                {
                    "name": name,
                    "id": v["id"],
                    "creator": creator_dto,
                    "date": v.get("date", None),
                }
            )
        return result

    # Pour l'onglet "Documents générés"
    def get_is_valid(self, obj: Demande) -> JSON:
        return obj.is_valid()

    # Pour l'onglet "historique"
    def get_past_versions(self, obj: Demande) -> JSON:
        return obj.past_versions or []

    def get_history(self, obj: Demande) -> JSON:
        return obj.wf_history

    # Workflow
    def get_possible_transitions(self, obj: Demande) -> JSON:
        user = get_current_profile()
        return obj.get_workflow(user).possible_transitions()


@singledispatch
def add_more_fields(demande: Demande, dto: JSONDict):
    return dto


@add_more_fields.register
def add_more_fields_rh(demande: DemandeRH, dto: JSONDict):
    dto["salaire_brut_mensuel"] = demande.data.get("salaire_brut_mensuel", None)
    dto["date_debut"] = demande.data.get("date_debut", None)
    dto["duree_mois"] = demande.duree_mois
    if not dto["acces_restreint"]:
        try:
            dto["cout_total_charge"] = float(demande.cout_total_charge)
        except ValueError:
            dto["cout_total_charge"] = 0
    return dto
