from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy import Column, String, Table
from sqlalchemy.orm import mapper

from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.services.roles import Role, RoleService


def new_id() -> str:
    return str(uuid.uuid1())


@dataclass
class Grant:
    id: str
    user_id: str
    role_name: str
    context_id: Optional[str]


def make_mapper(metadata):
    table = Table(
        "v3_grants",
        metadata,
        #
        Column("id", String(36), primary_key=True),
        Column("user_id", String(36), index=True, nullable=False),
        Column("role_name", String(64), index=True, nullable=False),
        Column("context_id", String(36), index=True),
    )

    mapper(Grant, table)


class SqlaRoleService(RoleService):
    profile_repository = ProfileRepository
    structure_repository = StructureRepository

    @inject
    def __init__(
        self,
        db: SQLAlchemy,
        profile_repository: ProfileRepository,
        structure_repository: StructureRepository,
    ):
        self.profile_repository = profile_repository
        self.structure_repository = structure_repository
        self.db = db
        self.session = self.db.session
        make_mapper(self.db.metadata)

    def is_empty(self):
        return self.session.query(Grant).count() == 0

    def clear(self):
        self.session.query(Grant).delete()
        self.session.flush()

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

    def get_grant(self, user, role, context) -> Grant:
        assert isinstance(user, Profile)
        assert isinstance(role, Role)

        if context:
            context_id = context.id
        else:
            context_id = None
        query = (
            self.session.query(Grant)
            .filter(Grant.user_id == user.id)
            .filter(Grant.role_name == role.name)
            .filter(Grant.context_id == context_id)
        )
        return query.first()

    def has_role(self, user: Profile, role: Role, context: Any = None):
        assert isinstance(user, Profile)
        assert isinstance(role, Role)

        if context:
            context_id = context.id
        else:
            context_id = None
        query = (
            self.session.query(Grant)
            .filter(Grant.user_id == user.id)
            .filter(Grant.role_name == role.name)
            .filter(Grant.context_id == context_id)
        )
        return query.count() > 0

    def get_users_with_role(self, role: Role, context: Any = None):
        assert isinstance(role, Role)

        if context:
            context_id = context.id
        else:
            context_id = None
        query = (
            self.session.query(Grant)
            .filter(Grant.role_name == role.name)
            .filter(Grant.context_id == context_id)
        )
        grants = query.all()

        user_ids = {g.user_id for g in grants}
        users = {self.profile_repository.get_by_id(user_id) for user_id in user_ids}
        return users

    def get_users_with_role_on(self, context: Structure) -> Dict[Role, Set[Profile]]:
        query = self.session.query(Grant).filter(Grant.context_id == context.id)
        grants = query.all()
        result: Dict[Role, Set] = defaultdict(set)
        for grant in grants:
            user = self.profile_repository.get_by_id(grant.user_id)
            role = getattr(Role, grant.role_name)
            result[role].add(user)
        return result

    def get_users_with_given_role(self, role: Role, context: Structure):
        assert isinstance(role, Role)

        query = (
            self.session.query(Grant)
            .filter(Grant.role_name == role.name)
            .filter(Grant.context_id == context.id)
        )
        grants = query.all()
        return {self.profile_repository.get_by_id(grant.user_id) for grant in grants}

    def get_roles_for_user(self, user: Profile) -> Dict[Role, Set[Structure]]:
        query = self.session.query(Grant).filter(Grant.user_id == user.id)
        grants = query.all()

        result = defaultdict(set)
        for grant in grants:
            context = self.structure_repository.get_by_id(grant.context_id)
            role = getattr(Role, grant.role_name)
            result[role].add(context)

        return result

    def update_roles(self, user: Profile):
        roles = self.get_roles_for_user(user)

        structures: Set[Structure]

        structures = roles[Role.MEMBRE]
        for structure in structures:
            self.ungrant_role(user, Role.MEMBRE, structure)

        structures = roles[Role.MEMBRE_AFFILIE]
        for structure in structures:
            self.ungrant_role(user, Role.MEMBRE_AFFILIE, structure)

        structures = roles[Role.MEMBRE_AFFECTE] | roles[Role.MEMBRE_RATTACHE]
        for structure in structures:
            self.grant_role(user, Role.MEMBRE, structure)

        ancestors = set()
        for structure in structures:
            ancestors.update(structure.ancestors)

        for structure in ancestors:
            self.grant_role(user, Role.MEMBRE_AFFILIE, structure)
            self.grant_role(user, Role.MEMBRE, structure)
