"""Methodes JSON-RPC pour manipuler le graphe des structures.

Note: les méthodes sont préfixées par "sg_" (sg = "structures graph").

Roles / Permissions:

Admin central:

- L’admin central est le seul qui peut créer des sous-structures dans des structures autres
  que les labos
- Seul l’admin central peut créer des structures virtuelles

cf. https://trello.com/c/cRUEKsVv/
"""
from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from werkzeug.exceptions import NotFound

from labster.auth import AuthContext
from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import Structure, StructureId, \
    StructureRepository
from labster.domain2.model.type_structure import get_type_structure_by_id
from labster.domain2.services.roles import RoleService
from labster.rbac import check_permission, check_structure_editable
from labster.rpc.cache import cache
from labster.types import JSON

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
auth_context = injector.get(AuthContext)
db = injector.get(SQLAlchemy)


@method
def sg_update_structure(id: str, model: dict[str, JSON]):
    structure = structure_repo.get_by_id(StructureId(id))
    check_structure_editable(structure)

    for k, v in model.items():
        setattr(structure, k, v)

    db.session.commit()
    cache.evict("structures")


@method
def sg_create_child_structure(id: str, model: dict[str, str]):
    parent_structure = structure_repo.get_by_id(StructureId(id))
    if not parent_structure:
        raise NotFound()

    check_permission(parent_structure, "P3")

    new_structure = Structure()
    new_structure.nom = model["nom"]
    type_structure = get_type_structure_by_id(model["type_id"])
    new_structure.type_name = type_structure.name

    parent_structure.add_child(new_structure)
    structure_repo.put(new_structure)

    db.session.commit()
    cache.evict("structures")


@method
def sg_delete_structure(id: str):
    structure = structure_repo.get_by_id(StructureId(id))
    if not structure:
        raise NotFound()

    check_permission(structure, "P3")

    structure.delete()

    db.session.commit()
    cache.evict("structures")


@method
def sg_add_edge(u_id, v_id):
    u = structure_repo.get_by_id(StructureId(u_id))
    v = structure_repo.get_by_id(StructureId(v_id))

    check_permission(u, "P3")

    u.add_child(v)

    db.session.commit()
    cache.evict("structures")


@method
def sg_delete_edge(u_id, v_id):
    u = structure_repo.get_by_id(StructureId(u_id))
    v = structure_repo.get_by_id(StructureId(v_id))

    check_permission(u, "P3")

    u.remove_child(v)

    db.session.commit()
    cache.evict("structures")
