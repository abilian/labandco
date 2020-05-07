from __future__ import annotations

import structlog
from abilian.core.extensions import csrf, db, login_manager
from flask_redis import FlaskRedis
from flask_smorest import Api
from werkzeug.exceptions import abort

from .mail import Mail
from .whoosh import Whoosh

logger = structlog.get_logger()

redis = FlaskRedis()
mail = Mail()
api = Api()
whoosh = Whoosh()

db = db

# Ensure that these import are not removed by PyCharm
assert db
assert login_manager


@csrf.error_handler
def csrf_error_response(reason):
    # let sentry be aware of csrf failures. They might show app is broken
    # somewhere
    logger.error("Csrf error report, reason: %s", reason, extra={"stack": True})
    return abort(400, reason)
