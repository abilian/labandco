"""
Methodes JSON-RPC pour manipuler le graphe des structures.

Note: les méthodes sont préfixées par "sg_" (sg = "structures graph").
"""
from __future__ import annotations

from typing import Dict

from jsonrpcserver import method
from werkzeug.exceptions import NotFound

from labster.auth import AuthContext
from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import Structure, StructureId, \
    StructureRepository
from labster.domain2.model.type_structure import get_type_structure_by_id
from labster.domain2.services.roles import RoleService
from labster.persistence import Persistence
from labster.rpc.cache import cache
from labster.types import JSON

from ..util import ensure_role

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)
role_service = injector.get(RoleService)
auth_context = injector.get(AuthContext)
persistence = injector.get(Persistence)


@method
def sg_update_structure(id: str, model: Dict[str, JSON]):
    ensure_role("alc")

    try:
        structure = structure_repo.get_by_id(StructureId(id))
        assert structure
    except (KeyError, AssertionError):
        raise NotFound()

    for k, v in model.items():
        setattr(structure, k, v)

    persistence.save()
    cache.evict("structures")


@method
def sg_create_child_structure(id: str, model: Dict[str, str]):
    ensure_role("alc")

    try:
        parent_structure = structure_repo.get_by_id(StructureId(id))
        assert parent_structure
    except (KeyError, AssertionError):
        raise NotFound()

    new_structure = Structure()
    new_structure.nom = model["nom"]
    type_structure = get_type_structure_by_id(model["type_id"])
    new_structure.type_name = type_structure.name

    parent_structure.add_child(new_structure)
    structure_repo.put(new_structure)

    persistence.save()
    cache.evict("structures")


@method
def sg_delete_structure(id: str):
    ensure_role("alc")

    structure = structure_repo.get_by_id(StructureId(id))
    assert structure

    structure.delete()

    persistence.save()
    cache.evict("structures")


@method
def sg_add_edge(u_id, v_id):
    # TODO: permissions
    ensure_role("alc")

    u = structure_repo.get_by_id(StructureId(u_id))
    v = structure_repo.get_by_id(StructureId(v_id))
    u.add_child(v)

    persistence.save()
    cache.evict("structures")


@method
def sg_delete_edge(u_id, v_id):
    # TODO: permissions
    ensure_role("alc")

    u = structure_repo.get_by_id(StructureId(u_id))
    v = structure_repo.get_by_id(StructureId(v_id))
    u.remove_child(v)

    persistence.save()
    cache.evict("structures")
