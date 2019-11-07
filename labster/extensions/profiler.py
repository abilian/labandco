from __future__ import annotations

import flask_profiler


def register_profiler(app):
    config = app.config

    if not config.get("PROFILER_ENABLE"):
        return

    password = config.get("PROFILER_PASSWORD")

    config["flask_profiler"] = {
        "enabled": True,
        "storage": {"engine": "sqlalchemy"},
        "ignore": ["^/static/.*"],
    }
    if password:
        config["flask_profiler"]["basicAuth"] = {
            "enabled": True,
            "username": "profiler",
            "password": password,
        }
    flask_profiler.init_app(app)
