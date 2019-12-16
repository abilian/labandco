from __future__ import annotations

import shelve

from flask import current_app, request
from flask_sqlalchemy import SQLAlchemy
from injector import Injector, inject

from labster.domain2.model.profile import ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.contacts import ContactService
from labster.domain2.services.roles import RoleService


class Persistence:
    def save(self):
        pass


class NoPersistence(Persistence):
    def save(self):
        pass


class SqlaPersistence(Persistence):
    @inject
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def save(self):
        self.db.session.commit()
