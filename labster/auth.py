from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from flask import g

from labster.domain2.model.profile import Profile

if TYPE_CHECKING:
    from labster.security import User, AuthenticatedUser


class AuthContext:
    _current_user = None
    _current_profile = None

    def authenticate(self, profile: Optional[Profile]):
        from labster.security import AuthenticatedUser

        if profile is None:
            self.clear()
        else:
            self._current_profile = profile
            self._current_user = AuthenticatedUser(profile)

    def clear(self):
        self._current_profile = None
        self._current_user = None

    @property
    def current_user(self) -> User:
        if self._current_user:
            return self._current_user

        try:
            return g.current_user
        except (RuntimeError, AttributeError):
            from labster.security import AnonymousUser

            return AnonymousUser()

    @property
    def current_profile(self) -> Optional[Profile]:
        if self._current_profile:
            return self._current_profile

        try:
            return g.current_profile
        except (RuntimeError, AttributeError):
            return None
