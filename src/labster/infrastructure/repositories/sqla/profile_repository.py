from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from labster.domain2.model.profile import Profile, ProfileId, ProfileRepository
from labster.infrastructure.repositories.sqla.mappers import Mapper


class SqlaProfileRepository(ProfileRepository):
    session: Session

    @inject
    def __init__(self, db: SQLAlchemy, mapper: Mapper):
        self.db = db
        self.session = db.session

    def query(self):
        return self.session.query(Profile)

    def get_all(self) -> set[Profile]:
        return set(self.query().all())

    def put(self, profile: Profile):
        if not profile.id:
            profile.id = ProfileId.new()
        self.session.add(profile)

    def delete(self, profile: Profile):
        self.session.delete(profile)

    def is_empty(self):
        return self.query().count() == 0

    def clear(self):
        self.query().delete()

    def get_by_id(self, id: ProfileId) -> Profile:
        result = self.query().get(id)
        if not result:
            raise NoResultFound
        return result

    def get_by_old_id(self, old_id: int) -> Profile:
        return self.query().filter_by(old_id=old_id).one()

    def get_by_login(self, login: str) -> Profile:
        return self.query().filter_by(login=login).one()

    def get_by_uid(self, uid: str) -> Profile:
        return self.query().filter_by(uid=uid).one()

    def get_by_old_uid(self, old_uid: str) -> Profile:
        return self.query().filter_by(old_uid=old_uid).one()
