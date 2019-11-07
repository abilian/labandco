from __future__ import annotations

from jsonrpcserver import method

from labster.auth import AuthContext
from labster.di import injector
from labster.domain2.services.demande import get_demande_types_for_user
from labster.domain2.services.roles import RoleService
from labster.types import JSON

auth_context = injector.get(AuthContext)
role_service = injector.get(RoleService)


@method
def get_home_data() -> JSON:
    assert auth_context.current_profile
    result = get_demande_types_for_user(auth_context.current_profile, role_service)
    return {
        "demande_types": list(result),
    }
