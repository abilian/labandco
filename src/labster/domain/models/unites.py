"""Modèle un peu simpliste de hiérarchie LDAP + info métiers spécifiques."""
from __future__ import annotations

from typing import TYPE_CHECKING

import toolz
from abilian.core.entities import Entity, EntityQuery
from abilian.core.sqlalchemy import JSONDict
from attr import attrib, attrs
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, \
    Unicode
from sqlalchemy.orm import backref, foreign, relationship, remote

from labster.domain.services import roles as roles_service
from labster.extensions import db

if TYPE_CHECKING:
    from .profiles import Profile
    from .roles import RoleType

# Constantes utilisées pour typer les OrgUnits
POLE_DE_RECHERCHE = "Pôle de recherche"
UFR = "UFR"
LABORATOIRE = "Laboratoire"
DEPARTEMENT = "Département"
EQUIPE = "Équipe"
BUREAU_DGRTT = "Bureau DGRTT"

TYPE_ENUM = [POLE_DE_RECHERCHE, UFR, LABORATOIRE, DEPARTEMENT, EQUIPE, BUREAU_DGRTT]

__all__ = (
    "OrgUnit",
    "POLE_DE_RECHERCHE",
    "UFR",
    "LABORATOIRE",
    "DEPARTEMENT",
    "EQUIPE",
    "BUREAU_DGRTT",
)


class OrgUnitQuery(EntityQuery):
    def filter_by_type(self, type):
        return self.filter(OrgUnit.type == type)

    def get_by_nom(self, nom):
        return self.filter(OrgUnit.nom == nom).one()

    def get_by_sigle(self, sigle):
        return self.filter(OrgUnit.sigle == sigle).one()

    def get_by_dn(self, dn):
        return self.filter(OrgUnit.dn == dn).one()

    def ufrs_count(self):
        return self.filter_by_type(UFR).count()

    def labos_count(self):
        return self.filter_by_type(LABORATOIRE).count()

    def filter_by_parent(self, parent):
        return self.filter(OrgUnit.parent_id == parent.id)


@attrs(init=False, these={"type": attrib(), "nom": attrib(), "id": attrib()}, hash=True)
class OrgUnit(Entity):
    __tablename__ = "orgunit"
    __indexable__ = False
    query_class = OrgUnitQuery

    type = Column(Enum(*TYPE_ENUM, name="orgunit_type"), nullable=False)

    dn = Column(String, unique=True, index=True)
    nom = Column(Unicode, nullable=False, unique=True)
    sigle = Column(Unicode, default="", nullable=False)

    parent_id = Column(Integer, ForeignKey("orgunit.id"))
    parent = relationship(
        "OrgUnit",
        primaryjoin=remote(Entity.id) == foreign(parent_id),
        backref=backref("children", lazy="joined", cascade="all, delete-orphan"),
    )

    wf_settings = Column(JSONDict(), default=dict)

    permettre_reponse_directe = Column(Boolean)
    permettre_soummission_directe = Column(Boolean)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.wf_settings = {}

    def __unicode__(self):
        return f"<OrgUnit type='{self.type}' nom='{self.nom}' id={self.id}>"

    __str__ = __unicode__

    # def __repr__(self):
    #     return unicode(self).encode('utf8')

    @property
    def sigle_ou_nom(self) -> str:
        return self.sigle or self.nom

    @property
    def depth(self) -> int:
        if self.type == EQUIPE:
            return 4
        if self.type == DEPARTEMENT:
            return 3
        if self.type == LABORATOIRE:
            return 2
        if self.type == UFR:
            return 1
        if self.type == POLE_DE_RECHERCHE:
            return 0
        # Should not happen
        return 0

    @property
    def path(self) -> list[str]:
        t = [""] * 5
        for p in self.parents + [self]:
            t[p.depth] = p.nom
        return t

    @property
    def parents(self) -> list[OrgUnit]:
        p = self
        result = []
        while True:
            p = p.parent
            if not p:
                break
            result.append(p)
        result.reverse()
        return result

    def descendants(self) -> list[OrgUnit]:
        if self.type == EQUIPE:
            return []
        if self.type == DEPARTEMENT:
            return list(self.children)

        children = self.children
        result = list(children)
        for c in children:
            result += c.descendants()
        return result

    def get_contacts_dgrtt(self):
        from .mapping_dgrtt import MappingDgrtt

        return MappingDgrtt.query.get_for_ou(self)

    def get_members_with_role(self, role_type: RoleType | None) -> list[Profile]:
        roles = roles_service.get_roles(role_type=role_type, target=self)
        result = [r.profile for r in roles if r.profile]
        return result

    def get_directeurs(self) -> list[Profile]:
        from .roles import RoleType

        result = self.get_members_with_role(RoleType.DIRECTION)
        assert all(p.has_role("directeur") for p in result)

        # On met le "vrai" directeur en premier
        result = [p for p in result if p.is_directeur] + [
            p for p in result if not p.is_directeur
        ]

        return result

    def get_gestionnaires(self) -> list[Profile]:
        from .roles import RoleType

        result = self.get_members_with_role(RoleType.GDL)
        assert all(p.has_role("gestionnaire") for p in result)
        return result

    def get_administrateurs(self) -> list[Profile]:
        from .roles import RoleType

        result = self.get_members_with_role(RoleType.ALL)
        assert all(p.has_role("all") for p in result)
        return result

    @property
    def direction(self) -> list[Profile]:
        return self.get_directeurs()

    @property
    def gestionnaires(self) -> list[Profile]:
        return self.get_gestionnaires()

    @property
    def administrateurs(self):
        return self.get_administrateurs()

    def set_roles(self, users: list[Profile], role_type: RoleType) -> None:
        roles = roles_service.get_roles(role_type=role_type, target=self)
        for role in roles:
            db.session.delete(role)
        db.session.flush()
        for user in users:
            roles_service.grant_role(user, role_type, self)

    @property
    def directeur(self) -> Profile | None:

        direction = self.get_directeurs()
        direction = [d for d in direction if d.is_directeur]
        return toolz.get(0, direction, None)

    @property
    def adresse(self):
        if self.directeur and self.directeur.adresse:
            return self.directeur.adresse
        return ""

    def validate(self) -> None:
        if self.type == POLE_DE_RECHERCHE:
            assert self.parent is None

        elif self.type == UFR:
            assert self.parent.type == POLE_DE_RECHERCHE

        elif self.type == LABORATOIRE:
            assert self.parent.type in (POLE_DE_RECHERCHE, UFR)

        elif self.type == DEPARTEMENT:
            assert self.parent.type == LABORATOIRE

        elif self.type == EQUIPE:
            assert self.parent.type in (LABORATOIRE, DEPARTEMENT)

        elif self.type == BUREAU_DGRTT:
            assert self.parent is None

        else:
            raise AssertionError()

    def get_labo(self) -> OrgUnit | None:
        if self.type == LABORATOIRE:
            return self
        if not self.parent:
            return None
        if self.parent.type == LABORATOIRE:
            return self.parent
        if self.parent.parent.type == LABORATOIRE:
            return self.parent.parent
        raise AssertionError("Should not happen")

    @property
    def laboratoire(self) -> OrgUnit | None:
        try:
            return self.get_labo()
        except Exception:
            return None

    @property
    def equipe(self) -> OrgUnit | None:
        if self.type == EQUIPE:
            return self
        return None

    @property
    def departement(self) -> OrgUnit | None:
        if self.type == DEPARTEMENT:
            return self
        if self.type == EQUIPE and self.parent.type == DEPARTEMENT:
            return self.parent
        return None

    @property
    def ufr(self) -> OrgUnit | None:
        if self.type == POLE_DE_RECHERCHE:
            return None
        if self.type == UFR:
            return self

        assert self.laboratoire
        labo: OrgUnit = self.laboratoire
        parent = labo.parent
        if parent.type == UFR:
            return parent
        return None

    @property
    def pole(self) -> OrgUnit | None:
        if self.type == POLE_DE_RECHERCHE:
            return self
        if self.type == UFR:
            return self.parent

        assert self.laboratoire
        labo: OrgUnit = self.laboratoire
        parent: OrgUnit = labo.parent
        if parent.type == POLE_DE_RECHERCHE:
            return parent
        return parent.parent

    def get_membres(self) -> list[Profile]:
        if self.type not in [LABORATOIRE, EQUIPE, DEPARTEMENT]:
            return []

        labo = self.get_labo()
        if labo:
            membres_du_labo = {m for m in labo.membres if m.active}
        else:
            membres_du_labo = set()

        if self.type == LABORATOIRE:
            membres = list(membres_du_labo)

        elif self.type == EQUIPE:
            membres = [m for m in membres_du_labo if m.sous_structure == self]

        else:
            # self.type == DEPARTEMENT
            membres_dict = {m for m in membres_du_labo if m.sous_structure == self}
            for equipe in self.children:
                membres_dict.update(equipe.get_membres())
            membres = list(membres_dict)

        def sorter(profile: Profile) -> tuple[str, str]:
            return profile.nom, profile.prenom

        return sorted(membres, key=sorter)

    def wf_must_validate(self, type: str) -> bool:
        assert type in [LABORATOIRE, DEPARTEMENT, EQUIPE]

        if self.type == LABORATOIRE:
            return True

        wf_settings = self.wf_settings
        if type == LABORATOIRE:
            return wf_settings.get("validation_labo", True)
        elif type == DEPARTEMENT:
            return wf_settings.get("validation_dept", True)
        else:
            # type == EQUIPE
            return wf_settings.get("validation_equipe", True)
