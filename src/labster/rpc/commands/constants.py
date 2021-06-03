from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from werkzeug.exceptions import BadRequest

from labster.di import injector
from labster.domain2.services.constants import save_constants

db = injector.get(SQLAlchemy)


@method
def update_constants(constants):
    if not constants:
        raise BadRequest()

    save_constants(constants)

    db.session.commit()
