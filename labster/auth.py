from __future__ import annotations

from typing import Optional

from flask import g

from labster.domain2.model.profile import Profile as NewProfile
from labster.domain.models.profiles import Profile


class AuthContext:
    @property
    def current_user(self) -> Optional[Profile]:
        try:
            return g.current_user
        except RuntimeError:
            return None

    @property
    def current_profile(self) -> Optional[NewProfile]:
        try:
            return g.current_profile
        except RuntimeError:
            return None
