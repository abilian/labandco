from __future__ import annotations

from typing import Any, Dict, List

from flask import g

from labster.di import injector
from labster.domain2.model.profile import ProfileRepository
from labster.domain2.services.roles import Role, RoleService

profile_repository = injector.get(ProfileRepository)
role_service = injector.get(RoleService)


class Node:
    _label = ""

    def __getitem__(self, key: str) -> Any:
        return getattr(self, "_" + key)

    def get(self, key: str, default=None) -> Any:
        return getattr(self, "_" + key, default)

    def is_active(self) -> bool:
        user = g.current_user
        required_roles = self.get("requires_role")

        if not required_roles:
            return True

        # XXX: Temp hack
        if isinstance(list(required_roles)[0], Role):
            if not hasattr(user, "uid"):
                return False
            profile = profile_repository.get_by_uid(user.uid)
            result = any(
                role_service.has_role(profile, role) for role in required_roles
            )

        else:
            result = any(user.has_role(role) for role in required_roles)
        return result

    def __repr__(self):
        return f"<Node label={self._label}>"


class MenuItem(Node):
    _url = ""
    _entries = []  # type: List[Dict]

    def __init__(self, specs: Dict[str, Any]):
        for k, v in specs.items():
            setattr(self, "_" + k, v)

    @property
    def url(self) -> str:
        if self._url:
            return self._url

        return "#"

    @property
    def entries(self) -> List[MenuItem]:
        return [MenuItem(entry) for entry in self._entries]

    def asdict(self):
        result = {}
        for k, v in vars(self).items():
            if k.startswith("_"):
                if isinstance(v, (list, dict, int, str, type(None))):
                    result[k[1:]] = v
        result["entries"] = [entry.asdict() for entry in self.entries]
        return result


class Menu(Node):
    _entries = []  # type: List[Dict]

    def __init__(self, specs: Dict) -> None:
        for k, v in specs.items():
            setattr(self, "_" + k, v)
        self.entries = [MenuItem(e) for e in self._entries]

    @property
    def active_entries(self) -> List[MenuItem]:
        if not self.is_active():
            return []
        # print("all:", [e for e in self.entries])
        result = [e for e in self.entries if e.is_active()]
        # print("after filtering:", result)
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
