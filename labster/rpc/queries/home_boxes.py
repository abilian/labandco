from __future__ import annotations

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


def get_boxes(archives=False) -> JSON:
    archives = bool(archives)
    user = get_current_profile()

    result = []
    for scope in SCOPES:
        table_view = get_table_view(scope, user, archives)
        if table_view:
            result.append(
                {"title": table_view.title, "scope": scope, "archives": archives}
            )

    return result
