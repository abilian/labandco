from __future__ import annotations

from functools import wraps

import structlog
from flask import g, redirect, session, url_for
from flask_login import AnonymousUserMixin
from werkzeug.exceptions import Forbidden

from labster.di import injector
from labster.domain2.model.profile import ProfileRepository

from .domain.models.profiles import Profile


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        current_user = g.current_user
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", _external=True))
        else:
            return func(*args, **kwargs)

    return decorated_view


def requires_role(role):
    def decorator(f):
        f._explict_rule_set = True

        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = g.current_user
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", _external=True))
            elif not current_user.has_role(role):
                raise Forbidden()
            return f(*args, **kwargs)

        return decorated_function

    return decorator


class AnonymousUser(AnonymousUserMixin):
    name = "Anonymous"

    def has_role(self, *args, **kw):
        return False


def login_user():
    current_user_id = session.get("current_user", "ANONYMOUS")
    logger = structlog.get_logger()

    if current_user_id == "ANONYMOUS":
        g.current_user = AnonymousUser()
        g.current_profile = None
        logger.new(user=None)

    else:
        try:
            user: Profile = Profile.query.get_by_uid(current_user_id)
            g.current_user = user

            profile_repos = injector.get(ProfileRepository)
            try:
                g.current_profile = profile_repos.get_by_login(current_user_id)
            except KeyError:
                g.current_profile = profile_repos.get_by_old_uid(user.uid)

        except KeyError:
            g.current_user = AnonymousUser()
            g.current_profile = None

        logger.new(user=g.current_user.name)
