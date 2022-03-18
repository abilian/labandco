from __future__ import annotations

from typing import TYPE_CHECKING

from flask import g

from labster.domain2.model.profile import Profile as NewProfile

if TYPE_CHECKING:
    from labster.security import User


class AuthContext:
    @property
    def current_user(self) -> User:
        try:
            return g.current_user
        except (RuntimeError, AttributeError):
            from labster.security import AnonymousUser

            return AnonymousUser()

    @property
    def current_profile(self) -> NewProfile | None:
        try:
            return g.current_profile
        except (RuntimeError, AttributeError):
            return None
