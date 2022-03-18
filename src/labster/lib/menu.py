from __future__ import annotations

from typing import Any

from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.services.roles import Role, RoleService
from labster.security import get_current_profile
from labster.util import url_for

profile_repository = injector.get(ProfileRepository)
role_service = injector.get(RoleService)


class Node:
    _label = ""

    def __getitem__(self, key: str) -> Any:
        return getattr(self, "_" + key)

    def get(self, key: str, default=None) -> Any:
        return getattr(self, "_" + key, default)

    def is_active(self) -> bool:
        profile = get_current_profile()
        required_roles = self.get("requires_role")
        precondition = self.get("precondition")

        if precondition:
            return precondition()

        if not required_roles:
            return True

        for role in required_roles:
            if role == "alc" and profile.has_role(Role.ADMIN_CENTRAL):
                return True

            if role == "directeur" and profile.has_role(Role.RESPONSABLE, "*"):
                return True

            if isinstance(role, Role) and profile.has_role(role):
                return True

        return False

    def __repr__(self):
        return f"<Node label={self._label}>"


class MenuItem(Node):
    _url = ""
    _endpoint = ""
    _entries: list[dict] = []

    def __init__(self, specs: dict[str, Any]):
        for k, v in specs.items():
            setattr(self, "_" + k, v)

    @property
    def url(self) -> str:
        if self._url:
            return self._url

        if self._endpoint:
            return url_for(self._endpoint)

        return ""

    @property
    def entries(self) -> list[MenuItem]:
        return [MenuItem(entry) for entry in self._entries]

    def asdict(self):
        result = {}

        for k, v in vars(self).items():
            if k.startswith("_"):
                if isinstance(v, (list, dict, int, str, type(None))):
                    result[k[1:]] = v

        result["url"] = self.url
        result["entries"] = [entry.asdict() for entry in self.entries]

        return result


class Menu(Node):
    _entries: list[dict] = []

    def __init__(self, specs: dict) -> None:
        for k, v in specs.items():
            setattr(self, "_" + k, v)
        self.entries = [MenuItem(e) for e in self._entries]

    @property
    def active_entries(self) -> list[MenuItem]:
        if not self.is_active():
            return []
        result = [e for e in self.entries if e.is_active()]
        return result

    def is_empty(self) -> bool:
        return len(self.active_entries) == 0

    def asdict(self):
        result = {}
        for k, v in vars(self).items():
            if k.startswith("_"):
                if isinstance(v, (list, dict, int, str, type(None))):
                    result[k[1:]] = v
        result["entries"] = [entry.asdict() for entry in self.active_entries]
        return result
