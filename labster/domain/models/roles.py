"""Tentative de modéliser les rôles de l'application sous forme de hiérarchie
de classes."""

from __future__ import annotations

import enum

from abilian.core.entities import Entity
from attr import attrib, attrs
from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from .profiles import Profile
from .unites import OrgUnit


class RoleType(enum.Enum):
    MEMBRE = "Membre"
    GDL = "Gestionnaire de demande Labster"
    DIRECTION = "Direction"
    PORTEUR = "Porteur"
    ALL = "Administrateur Labster local"

    CONTACT_DGRTT = "Contact DGRTT"
    CHEF_DE_BUREAU_DGRTT = "Chef de bureau DGRTT"
    ALC = "Administrateur Labster central"


TYPE_ENUM = [t.value for t in list(RoleType)]


@attrs(init=False, these={"type": attrib(), "context": attrib()}, hash=True)
class Role(Entity):
    # __tablename__ = 'role'
    __indexable__ = False

    type = Column(Enum(*TYPE_ENUM, name="role_type"), nullable=False)

    profile_id = Column(Integer, ForeignKey(Profile.id), index=True)
    profile = relationship(
        Profile,
        foreign_keys=[profile_id],
        backref=backref("roles", cascade="all,delete"),
    )

    context_id = Column(Integer, ForeignKey(OrgUnit.id), index=True)
    context = relationship(
        OrgUnit,
        foreign_keys=[context_id],
        backref=backref("contexts", cascade="all,delete"),
    )

    # def can(self, action, target):
    #   pass

    def __unicode__(self):
        if self.context:
            return "<{} de la structure: {} ({})>".format(
                self.type, self.context.nom, self.context.type
            )
        else:
            return f"<{self.type}>"
