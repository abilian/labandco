from __future__ import annotations

from typing import Set

from abilian.core.sqlalchemy import JSON
from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy import Boolean, Column, Integer, String, Table
from sqlalchemy.orm import Session, mapper

from labster.domain2.model.profile import Profile, ProfileId, ProfileRepository


def make_mapper(metadata):
    profiles = Table(
        "v3_profiles",
        metadata,
        #
        Column("id", String(36), primary_key=True),
        Column("uid", String(64), nullable=False),
        Column("old_id", Integer),
        Column("old_uid", String(64), default="", nullable=False),
        Column("login", String(64), default="", nullable=False),
        #
        Column("nom", String, default="", nullable=False),
        Column("prenom", String, default="", nullable=False),
        Column("email", String, default="", nullable=False),
        Column("adresse", String, default="", nullable=False),
        Column("telephone", String, default="", nullable=False),
        #
        Column("active", Boolean, default=False, nullable=False),
        Column("affectation", String, default="", nullable=False),
        Column("fonctions", JSON, nullable=False),
        #
        Column("preferences_notifications", Integer, default=0, nullable=False),
    )

    mapper(Profile, profiles)


class SqlaProfileRepository(ProfileRepository):
    session: Session

    @inject
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.session = self.db.session
        make_mapper(self.db.metadata)

    def get_all(self) -> Set[Profile]:
        return set(self.session.query(Profile).all())

    def put(self, profile: Profile):
        if not profile.id:
            profile.id = ProfileId.new()
        self.session.add(profile)

    def delete(self, profile: Profile):
        self.session.delete(profile)

    def is_empty(self):
        return self.session.query(Profile).count() == 0

    def clear(self):
        self.session.query(Profile).delete()
        self.session.flush()

    def get_by_id(self, id: ProfileId) -> Profile:
        return self.session.query(Profile).get(id)

    # TODO:
    # def get_by_uid(self, uid: str) -> Profile:
    #
    # def get_by_old_id(self, old_id: int) -> Profile:
    #
    # def get_by_login(self, login: str) -> Profile:
