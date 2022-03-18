from __future__ import annotations

from abc import ABC, ABCMeta
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from abilian.app import db
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String

from labster.domain2.model.base import Repository
from labster.ldap.constants import DRI_DN

if TYPE_CHECKING:
    from labster.domain2.model.structure import Structure
    from labster.domain2.services.roles import Role


FLUX_TENDU = 0
DAILY = 1
WEEKLY = 2


class ProfileId(str):
    @staticmethod
    def new() -> ProfileId:
        return ProfileId(uuid4())


# @attrs(eq=False, order=False, repr=False, auto_attribs=True)
class Profile(db.Model):
    __tablename__ = "v3_profiles"

    id = Column(String(36), primary_key=True)

    uid = Column(String(64), unique=True, nullable=True)
    old_id = Column(Integer, unique=True, nullable=True)
    old_uid = Column(String(64), unique=True, nullable=True)
    login = Column(String(64), default="", nullable=False)

    nom = Column(String, default="", nullable=False)
    prenom = Column(String, default="", nullable=False)
    email = Column(String, default="", nullable=False)
    adresse = Column(String, default="", nullable=False)
    telephone = Column(String, default="", nullable=False)

    active = Column(Boolean, default=False, nullable=False)
    affectation = Column(String, default="", nullable=False)
    fonctions = Column(JSON, nullable=False)

    preferences_notifications = Column(Integer, default=0, nullable=False)
    preferences_nb_jours_notifications = Column(Integer, default=0)

    date_derniere_notification_vue = Column(DateTime, default=datetime.utcnow)

    def __init__(self, **kw):
        self.id = str(uuid4())
        self.nom = ""
        self.prenom = ""
        self.fonctions = []
        super().__init__(**kw)

    def __str__(self):
        return f"<Profile {self.full_name}>"

    def __repr__(self):
        return str(self)

    @property
    def full_name(self):
        return self.prenom + " " + self.nom

    @property
    def reversed_name(self):
        return f"{self.nom}, {self.prenom}"

    @property
    def name(self):
        return self.full_name

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    #
    # Roles
    #
    def structure_d_appartenance(self) -> Structure:
        from labster.di import injector
        from labster.domain2.services.roles import Role, RoleService

        role_service = injector.get(RoleService)
        roles_dict = role_service.get_roles_for_user(self)
        structures = roles_dict[Role.MEMBRE_AFFECTE]
        assert len(structures) == 1
        return list(structures)[0]

    def has_role(self, role: Role, context: Any = None) -> bool:
        from labster.di import injector
        from labster.domain2.services.roles import RoleService

        role_service = injector.get(RoleService)
        return role_service.has_role(self, role, context)

    def is_membre_dri(self):
        from labster.di import injector
        from labster.domain2.model.structure import StructureRepository
        from labster.domain2.services.roles import Role

        structure_repo = injector.get(StructureRepository)
        dri = structure_repo.get_by_dn(DRI_DN)
        return self.has_role(Role.MEMBRE, dri)


class ProfileRepository(Repository, ABC, metaclass=ABCMeta):
    def get_all(self) -> set[Profile]:
        raise NotImplementedError

    def put(self, profile: Profile):
        raise NotImplementedError

    def delete(self, profile: Profile):
        raise NotImplementedError

    def get_by_id(self, id: ProfileId) -> Profile:
        raise NotImplementedError

    def get_by_uid(self, uid: str) -> Profile:
        raise NotImplementedError

    def get_by_old_id(self, old_id: int) -> Profile:
        raise NotImplementedError

    def get_by_login(self, login: str) -> Profile:
        raise NotImplementedError

    def get_by_old_uid(self, old_uid: str) -> Profile:
        raise NotImplementedError
