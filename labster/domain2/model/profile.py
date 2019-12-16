from __future__ import annotations

from abc import ABC, ABCMeta
from typing import TYPE_CHECKING, Any, List, Optional, Set
from uuid import uuid4

from attr import attrs

from labster.domain2.model.base import Repository

if TYPE_CHECKING:
    from labster.domain2.services.roles import Role


class ProfileId(str):
    @staticmethod
    def new() -> ProfileId:
        return ProfileId(uuid4())


@attrs(eq=False, order=False, repr=False, auto_attribs=True)
class Profile:
    id: ProfileId = ProfileId("")

    uid: Optional[str] = None
    login: str = ""

    old_id: Optional[int] = None
    old_uid: Optional[str] = None

    active: bool = True

    nom: str = ""
    prenom: str = ""
    email: str = ""
    adresse: str = ""
    telephone: str = ""

    affectation: str = ""
    fonctions: List[str] = []

    #: FLUX_TENDU = 0
    #: DAILY = 1
    #: WEEKLY = 2
    preferences_notifications: int = 0

    # #: Membre de la gouvernance ?
    # gouvernance = Column(Boolean)
    #
    # #: A vraiment les droits de la gouvernance
    # gouvernance_vraiment = Column(Boolean)
    #
    # #: Membre de la DGRTT
    # dgrtt = Column(Boolean)
    # chef_du_bureau = Column(Unicode)
    #
    # #: LDAP stuff
    # fonction_structurelle_principale = Column(Unicode)
    # #: More LDAP stuff
    # ldap_entry = Column(String)
    #
    # date_derniere_notification_vue = Column(
    #     DateTime, default=datetime.utcnow, nullable=False)
    #

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

    def has_role(self, role: Role, context: Any = None) -> bool:
        from labster.domain2.services.roles import RoleService
        from labster.di import injector

        role_service = injector.get(RoleService)
        return role_service.has_role(self, role, context)


class ProfileRepository(Repository, ABC, metaclass=ABCMeta):
    # @abstractmethod
    def get_all(self) -> Set[Profile]:
        raise NotImplementedError

    # @abstractmethod
    def put(self, profile: Profile):
        raise NotImplementedError

    # @abstractmethod
    def delete(self, profile: Profile):
        raise NotImplementedError

    #
    # Default (slow) implems
    #
    def get_by_id(self, id: ProfileId) -> Profile:
        # assert isinstance(id, ProfileId)

        for user in self.get_all():
            if user.id == id:
                return user
        raise KeyError(id)

    def get_by_uid(self, uid: str) -> Profile:
        for user in self.get_all():
            if user.uid == uid:
                return user
        raise KeyError(uid)

    def get_by_old_id(self, old_id: int) -> Profile:
        all = self.get_all()
        for x in all:
            if x.old_id == old_id:
                return x
        raise KeyError(old_id)

    def get_by_login(self, login: str) -> Profile:
        all = self.get_all()
        for x in all:
            if x.login == login:
                return x
        raise KeyError(login)

    def get_by_old_uid(self, old_uid: str) -> Profile:
        all = self.get_all()
        for x in all:
            if x.old_uid == old_uid:
                return x
        raise KeyError(old_uid)
