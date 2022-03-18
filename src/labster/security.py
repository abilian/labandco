from __future__ import annotations

from functools import wraps
from typing import Union

import structlog
from flask import g, redirect, session, url_for
from flask_login import AnonymousUserMixin, UserMixin

from labster.auth import AuthContext
from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        current_user = get_current_user()
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", _external=True))

        return func(*args, **kwargs)

    return decorated_view


class AnonymousUser(AnonymousUserMixin):
    name = "Anonymous"

    def has_role(self, *args, **kw):
        return False


class AuthenticatedUser(UserMixin):
    profile: Profile

    def __init__(self, profile):
        self.profile = profile

    @property
    def name(self):
        return self.profile.name

    @property
    def uid(self):
        return self.profile.uid


User = Union[AuthenticatedUser, AnonymousUser]


def login_user():
    current_user_id = session.get("current_user_id", "ANONYMOUS")
    logger = structlog.get_logger()

    if current_user_id == "ANONYMOUS":
        g.current_user = AnonymousUser()
        g.current_profile = None
        logger.new(user=None)

    else:
        try:
            profile_repos = injector.get(ProfileRepository)
            profile = profile_repos.get_by_id(current_user_id)

            g.current_profile = profile
            g.current_user = AuthenticatedUser(profile)

        except:
            g.current_user = AnonymousUser()
            g.current_profile = None

        logger.new(user=g.current_user.name)


def get_current_user() -> User:
    auth_context = injector.get(AuthContext)
    user = auth_context.current_user
    assert user
    return user


def get_current_profile() -> Profile:
    auth_context = injector.get(AuthContext)
    profile = auth_context.current_profile
    assert profile
    return profile
