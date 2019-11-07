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
    def load(self):
        pass

    def save(self):
        pass

    def mark_dirty(*objs):
        pass


class NoPersistence(Persistence):
    def load(self):
        pass

    def save(self):
        pass

    def mark_dirty(*objs):
        pass


class SqlaPersistence(Persistence):
    @inject
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def load(self):
        pass

    def save(self):
        self.db.session.commit()

    def mark_dirty(*objs):
        pass


def DummyPersistence(Persistence):
    @inject
    def __init__(self, injector: Injector):
        structure_repository = injector.get(StructureRepository)
        profile_repository = injector.get(ProfileRepository)
        role_service = injector.get(RoleService)
        contact_service = injector.get(ContactService)

        self.OBJECTS = [
            structure_repository,
            profile_repository,
            role_service,
            contact_service,
        ]

    def load(self):
        try:
            path = request.path
        except RuntimeError:
            path = None

        if path and path.startswith("/static/"):
            return
        if path and path.startswith("/_"):
            return

        while True:
            try:
                db = shelve.open("data/shelve")
                break
            except BaseException:
                pass

        for obj in self.OBJECTS:
            class_name = obj.__class__.__name__
            if obj.is_empty() and class_name in db:
                obj.set_state(db[class_name])

        db.close()

    def save(self):
        try:
            if current_app.config.get("TESTING"):
                return
        except RuntimeError:
            return

        db = shelve.open("data/shelve")

        for obj in self.OBJECTS:
            class_name = obj.__class__.__name__
            if obj.is_dirty:
                state = obj.get_state()
                db[class_name] = state

        db.close()

    def mark_dirty(self, *objs):
        for obj in objs:
            obj.is_dirty = True
