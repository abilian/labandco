from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import joinedload, mapper, relationship

from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.domain2.services.roles import Role, RoleService


def new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class Grant:
    id: str
    user_id: str
    role_name: str
    context_id: str | None


def make_mapper(metadata):
    table = Table(
        "v3_grants",
        metadata,
        #
        Column("id", String(36), primary_key=True),
        Column("user_id", String(36), ForeignKey(Profile.id), index=True),
        Column("role_name", String(64), index=True, nullable=False),
        Column("context_id", String(36), ForeignKey(Structure.id), index=True),
    )

    mapper(
        Grant,
        table,
        properties={"context": relationship(Structure), "user": relationship(Profile)},
    )


class SqlaRoleService(RoleService):
    @inject
    def __init__(
        self,
        db: SQLAlchemy,
    ):
        self.db = db
        self.session = self.db.session
        make_mapper(self.db.metadata)

    def query(self):
        return self.session.query(Grant)

    def is_empty(self):
        return self.query().count() == 0

    def clear(self):
        self.query().delete()

    def grant_role(self, user: Profile, role: Role, context: Any = None):
        grant = self.get_grant(user, role, context)
        if grant:
            return

        if context:
            grant = Grant(new_id(), user.id, role.name, context.id)
        else:
            grant = Grant(new_id(), user.id, role.name, None)

        self.session.add(grant)
        self.session.flush()

    def ungrant_role(self, user: Profile, role: Role, context: Any = None):
        grant = self.get_grant(user, role, context)
        if grant:
            self.session.delete(grant)
            self.session.flush()

    def get_grant(self, user: Profile, role: Role, context) -> Grant:
        assert isinstance(user, Profile)
        assert isinstance(role, Role)

        if context:
            context_id = context.id
        else:
            context_id = None
        query = (
            self.query()
            .filter_by(user_id=user.id)
            .filter_by(role_name=role.name)
            .filter_by(context_id=context_id)
        )
        return query.first()

    def has_role(self, user: Profile, role: Role, context: Any = None):
        assert context in ("*", None) or isinstance(context, Structure), str(context)

        if context == "*":
            query = (
                self.query().filter_by(user_id=user.id).filter_by(role_name=role.name)
            )
            return query.first() is not None
        else:
            return self.get_grant(user, role, context) is not None

    def get_users_with_role(self, role: Role, context: Any = None) -> set[Profile]:
        assert isinstance(role, Role)

        query = self.query().filter_by(role_name=role.name)
        if isinstance(context, Structure):
            query = query.filter_by(context_id=context.id)
        elif context is None:
            query = query.filter_by(context_id=None)
        elif context == "*":
            pass
        else:
            raise TypeError(f"Illegal argument for context: {context}")

        grants = query.options(joinedload(Grant.user)).all()
        return {grant.user for grant in grants}

    def get_users_with_role_on(self, context: Structure) -> dict[Role, set[Profile]]:
        query = self.query().filter_by(context_id=context.id)
        grants = query.all()

        result: dict[Role, set] = defaultdict(set)
        for grant in grants:
            role = getattr(Role, grant.role_name)
            result[role].add(grant.user)

        return result

    def get_users_with_given_role(self, role: Role, context: Structure) -> set[Profile]:
        assert isinstance(role, Role)
        assert isinstance(context, Structure)

        query = self.query().filter(Grant.context_id == context.id)
        if role == Role.MEMBRE:
            query = query.filter(
                Grant.role_name.in_(
                    [
                        Role.MEMBRE.name,
                        Role.MEMBRE_AFFILIE.name,
                        Role.MEMBRE_AFFECTE.name,
                        Role.MEMBRE_RATTACHE.name,
                    ]
                )
            )
        else:
            query = query.filter(Grant.role_name == role.name)
        grants = query.all()
        return {grant.user for grant in grants}

    def get_roles_for_user(self, user: Profile) -> dict[Role, set[Structure]]:
        query = self.query().filter_by(user_id=user.id)
        grants = query.all()

        result = defaultdict(set)
        for grant in grants:
            role = getattr(Role, grant.role_name)
            structure = grant.context
            if structure and not structure.active:
                continue
            result[role].add(structure)

        return result
