from __future__ import annotations

from typing import Any, Dict, Set

from labster.domain2.model.profile import Profile
from labster.domain2.model.type_structure import CA, CO, DE, DF, DU, ED, EQ, \
    FA, GRC, IN, LA, LX, SF, UN
from labster.domain2.services.roles import Role, RoleService

REC = object()
CON = object()
PI = object()

MAP: Dict[Any, Set[Any]] = {
    UN: {REC},
    FA: {REC},
    DU: {REC},
    CO: {REC, CON, PI},
    SF: {REC},
    DF: {REC},
    LA: {REC, CON, PI},
    ED: {REC, CON, PI},
    DE: set(),
    EQ: set(),
    CA: {REC, CON, PI},
    LX: {REC, CON, PI},
    IN: {REC, CON, PI},
    GRC: {REC, CON, PI},
}


def get_demande_types_for_user(user: Profile, role_service: RoleService) -> Set[str]:
    roles = role_service.get_roles_for_user(user)
    structures = roles.get(Role.PORTEUR, set()) | roles.get(Role.GESTIONNAIRE, set())

    result = {"autre", "faq"}
    for s in structures:
        x = MAP[s.type]
        if REC in x:
            result |= {"rh"}
        if PI in x:
            result |= {"pi_invention", "pi_logiciel"}
        if CON in x:
            result |= {"convention", "avenant_convention"}

    return result
