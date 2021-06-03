from __future__ import annotations

from labster.di import injector
from labster.domain2.services.roles import Role, RoleService
from labster.rpc.queries.demandes_tables import get_table_view
from labster.security import get_current_profile
from labster.types import JSON

SCOPES = [
    # DR&I
    "contact",
    "mes structures dri",
    "dri",
    "drv",
    # Autres structures
    "porteur",
    "gestionnaire",
    "mes structures",
]

SCOPES_RESPONSABLE = [
    # DR&I
    "contact",
    "mes structures dri",
    "dri",
    "drv",
    # Autres structures
    "mes structures",
    "porteur",
    "gestionnaire",
]


role_service = injector.get(RoleService)


def get_boxes(archives=False) -> JSON:
    archives = bool(archives)
    user = get_current_profile()

    if role_service.has_role(user, Role.RESPONSABLE, "*"):
        scopes = SCOPES_RESPONSABLE
    else:
        scopes = SCOPES
    result = []
    for scope in scopes:
        table_view = get_table_view(scope, user, archives)
        if table_view:
            result.append(
                {"title": table_view.title, "scope": scope, "archives": archives}
            )

    return result
