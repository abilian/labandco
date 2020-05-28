from __future__ import annotations

import os
import tempfile
from pathlib import Path

from flask import Blueprint, Flask, request, send_file
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from labster.auth import AuthContext
from labster.domain2.services.roles import Role

blueprint = Blueprint("backup", __name__, url_prefix="/backup")
route = blueprint.route

__all__ = ()

ROOT = "/home/labster"


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


@route("/file/")
def backup_file(app: Flask, auth_context: AuthContext):
    check_admin(auth_context)

    path_arg = request.args.get("path", "")
    path = Path(ROOT) / path_arg
    path = path.resolve()

    if not str(path).startswith(ROOT):
        raise BadRequest()

    if not path.exists():
        raise NotFound()

    if path.is_dir():
        files = list(path.glob("*"))
        files.sort()
        result = [f"<a href='.?path={file}'>{file}</a>" for file in files]
        return "<br>\n".join(result), {"content-type": "text/html"}

    else:
        fp = path.open("rb")
        return send_file(fp, as_attachment=True, attachment_filename=path.name)


def check_admin(auth_context: AuthContext):
    user = auth_context.current_profile
    assert user

    if not user.has_role(Role.ADMIN_CENTRAL):
        raise Forbidden()
