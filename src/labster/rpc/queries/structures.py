"""Methodes JSON-RPC pour manipuler le graphe des structures.

Note: les méthodes sont préfixées par "sg_" (sg = "structures graph").
"""
from __future__ import annotations

from collections.abc import Collection, Sequence

from jsonrpcserver import method
from marshmallow import Schema, fields
from marshmallow_sqlalchemy import ModelSchema
from werkzeug.exceptions import NotFound

from labster import rbac
from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import Structure, StructureId, \
    StructureRepository
from labster.domain2.model.type_structure import ALL_TYPES, DE, EQ
from labster.domain2.services.roles import Role, RoleService
from labster.rbac import has_permission
from labster.rpc.cache import cache
from labster.security import get_current_profile, get_current_user
from labster.types import JSON
from labster.util import sort_by_name

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)


@method
@cache.memoize(tag="structures", expire=3600)
def sg_all_structures() -> JSON:
    root = structure_repo.get_root()
    assert root

    def children(structure: Structure, level=0) -> list[tuple[Structure, int]]:
        assert structure

        result = [(structure, level)]
        my_children = list(structure.children)
        my_children.sort(key=lambda x: x.nom)
        for child in my_children:
            result += children(child, level + 1)
        return result

    structures2 = children(root, 0)

    entries = []
    for structure, level in structures2:
        structure_dto = {
            "id": structure.id,
            "nom": structure.nom,
            "sigle": structure.sigle,
            "type": structure.type_name,
            "level": level,
            "children_ids": [child.id for child in structure.children],
        }
        entries.append(structure_dto)

    return entries


@method
def sg_get_structure(structure_id) -> JSON:
    structure = structure_repo.get_by_id(StructureId(structure_id))
    if not structure:
        raise NotFound()

    ou_dto = FullStructureSchema().dump(structure).data
    ou_dto["parents"] = convert_structures_to_dto(list(structure.parents))
    ou_dto["children"] = convert_structures_to_dto(sort_by_name(structure.children))
    ou_dto["ancestors"] = convert_structures_to_dto(structure.ancestors)

    return ou_dto


@method
def sg_structure_can_be_deleted(id: str):
    structure = structure_repo.get_by_id(id)
    if not structure:
        raise NotFound()
    return has_permission(structure, "P3")


@method
def sg_get_possible_child_types(id: str) -> list[dict[str, str]]:
    user = get_current_profile()

    structure = structure_repo.get_by_id(id)
    if not structure:
        raise NotFound()

    if not has_permission(structure, "P3"):
        return []

    result = []
    for candidate_type in ALL_TYPES:
        if candidate_type.reel:
            continue
        if structure.type.can_have_child_of_type(candidate_type):
            if user.has_role(Role.ADMIN_CENTRAL):
                result.append({"value": candidate_type.id, "text": candidate_type.name})
            elif candidate_type in [DE, EQ]:
                result.append({"value": candidate_type.id, "text": candidate_type.name})

    return result


@method
def sg_get_parents_options(id):
    structure = structure_repo.get_by_id(id)
    if not structure:
        raise NotFound()

    if not has_permission(structure, "P2"):
        return []

    result = []
    for s in possible_parents(structure, structure_repo):
        if s.sigle:
            text = f"{s.type}: {s.name} ({s.sigle})"
        else:
            text = f"{s.type}: {s.name}"
        result.append({"text": text, "value": s.id})

    return sorted(result, key=lambda x: x["text"])


@method
def sg_get_children_options(id) -> JSON:
    structure = structure_repo.get_by_id(id)
    if not structure:
        raise NotFound()

    if not has_permission(structure, "P2"):
        return []

    result = []
    for s in possible_children(structure, structure_repo):
        if s.sigle:
            text = f"{s.type}: {s.name} ({s.sigle})"
        else:
            text = f"{s.type}: {s.name}"
        result.append({"text": text, "value": s.id})

    return sorted(result, key=lambda x: x["text"])


#
# Utils
#
def possible_parents(
    structure: Structure, repo: StructureRepository
) -> Collection[Structure]:
    s1 = repo.get_all()
    s2 = [s for s in s1 if structure.can_have_parent(s)]
    s3 = set(s2) - set(structure.parents)
    return s3


def possible_children(
    structure: Structure, repo: StructureRepository
) -> Collection[Structure]:
    s1 = repo.get_all()
    s2 = [s for s in s1 if structure.can_have_child(s)]
    s3 = set(s2) - set(structure.children)
    return s3


#
# Serialization
#
class FullStructureSchema(ModelSchema):
    is_reelle = fields.Bool()
    _depth = fields.Integer()
    can_be_deleted = fields.Method("_can_be_deleted")
    permissions = fields.Method("get_permissions")

    class Meta:
        model = Structure
        exclude = ["parents", "children"]

    def _can_be_deleted(self, structure):
        if structure.children:
            return False

        if role_service.get_users_with_given_role(Role.MEMBRE, structure):
            return False

        # For tests
        current_user = get_current_user()
        if not current_user.is_authenticated:
            return True

        profile = current_user.profile
        if profile.has_role(Role.ADMIN_CENTRAL):
            return True

        if structure.type in {DE, EQ}:
            if profile.has_role(Role.ADMIN_LOCAL, structure.parent) or profile.has_role(
                Role.ADMIN_LOCAL, structure.parent.parent
            ):

                return True

        return False

    def get_permissions(self, structure: Structure) -> dict[str, bool]:
        return {p: True for p in rbac.get_permissions_for_structure(structure)}


def convert_structures_to_dto(structures: Sequence[Structure]) -> JSON:
    class StructureSchema(Schema):
        id = fields.String()
        type = fields.String()
        nom = fields.String()
        sigle = fields.String()
        name = fields.String(attribute="sigle_ou_nom")

    return StructureSchema().dump(structures, many=True).data
