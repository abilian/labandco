from __future__ import annotations

import os
import tempfile

from flask import Blueprint, Flask, send_file
from werkzeug.exceptions import Forbidden

from labster.auth import AuthContext
from labster.domain2.services.roles import Role

blueprint = Blueprint("backup", __name__, url_prefix="/backup")
route = blueprint.route

__all__ = ()


@route("/db")
def backup_db(app: Flask, auth_context: AuthContext):
    check_admin(auth_context)

    config = app.config
    if "PG_PASSWORD" in config:
        os.putenv("PGUSER", "labster")
        os.putenv("PGPASSWORD", config["PG_PASSWORD"])

    fd, name = tempfile.mkstemp()
    status = os.system(f"pg_dump -F c labster > {name}")
    assert status == 0
    os.unlink(name)
    fp = os.fdopen(fd, "rb")
    return send_file(fp, as_attachment=True, attachment_filename="labster.dump")


def check_admin(auth_context: AuthContext):
    user = auth_context.current_profile
    assert user

    if not user.has_role(Role.ADMIN_CENTRAL):
        raise Forbidden()
