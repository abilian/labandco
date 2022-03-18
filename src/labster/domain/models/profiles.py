"""Modèle un peu simpliste de hiérarchie LDAP + info métiers spécifiques."""
from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

import ramda as r
import structlog
from abilian.core.entities import Entity, EntityQuery
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, \
    String, Unicode, text
from sqlalchemy.orm import relationship

from labster.domain.services import dgrtt as dgrtt_service
from labster.domain.services.roles import all_roles, get_roles, has_role, \
    set_role_value

from .unites import OrgUnit
from .workflow import EN_VALIDATION

if TYPE_CHECKING:
    from .demandes import Demande
    from .roles import Role


__all__ = ("Profile", "FLUX_TENDU", "DAILY", "WEEKLY")

logger = structlog.get_logger()

FLUX_TENDU = 0
DAILY = 1
WEEKLY = 2


class RolesMixin:
    def has_role(self, role, target=None):
        # type: (Any, Any) -> bool
        """Return True if profile has given role on given target."""
        if isinstance(role, (list, tuple, set)):
            return any(self.has_role(r, target) for r in role)
        return has_role(self, role, target)  # type: ignore

    def all_roles(self):
        return all_roles(self)

    def get_roles(self, type=None):
        return get_roles(self, type)

    def set_role_value(self, role: str, value: bool, target=None):
        return set_role_value(self, role, value, target)

    def set_default_roles(self):
        self.set_role_recherche()
        self.set_role_dgrtt()

    def set_role_recherche(self):
        roles = self.ldap_dict.get("eduPersonAffiliation")
        if "faculty" in roles or "researcher" in roles:
            self.set_role_value("porteur", True)

    def set_role_dgrtt(self):
        if self.has_role("dgrtt"):
            self.set_role_value("contact dgrtt", True)
        else:
            self.set_role_value("contact dgrtt", False)


class ChercheurMixin:
    """Méthodes spécifiques au rôle "chercheur"."""

    @property
    def contacts_dgrtt(self) -> list[tuple[str, str, Profile]]:
        """Return a list of tuples: (bureau.id, bureau.nom, contact)"""
        from labster.domain.models.mapping_dgrtt import MappingDgrtt

        labo = self.laboratoire  # type: ignore
        mapping_dgrtt = MappingDgrtt.query.filter(
            MappingDgrtt.ou_recherche == labo
        ).all()

        result = []
        for bureau in dgrtt_service.BUREAUX_DGRTT:
            if bureau.id in ["AIPI 2", "Com", "Finance 2", "Finance 3", "Moyens"]:
                continue

            for m in mapping_dgrtt:
                if m.bureau_dgrtt == bureau.id:
                    result.append((bureau.id, bureau.nom, m.contact_dgrtt))
                    break
        return result


class DirectionRechercheMixin:
    """Méthodes spécifiques au rôle "direction de recherche"."""

    @property
    def stucture_dont_je_suis_le_directeur(self) -> OrgUnit | None:
        from labster.domain.models.roles import RoleType

        roles = self.get_roles(RoleType.DIRECTION)  # type: ignore
        if len(roles) > 1:
            uid = self.uid  # type: ignore
            logger.error(f"L'utilisateur {uid} a plusieurs roles de direction")
        if not roles:
            return None
        return roles[0].context

    def demandes_a_valider(self) -> list[Demande]:
        demandes = self.mes_taches()  # type: ignore
        return [d for d in demandes if d.wf_state == EN_VALIDATION.id]


class GestionnaireMixin:
    def get_membres_de_mes_structures(self) -> list[Profile]:
        from .roles import RoleType

        roles = self.get_roles(RoleType.GDL)  # type: ignore
        membres: set[Profile] = set()
        for role in roles:
            org = role.context
            membres.update(org.get_membres())

        return r.sort_by(lambda x: x.nom, list(membres))


class RechercheMixin(ChercheurMixin, DirectionRechercheMixin):
    roles: list[Role]
    laboratoire: OrgUnit

    @property
    def structure(self) -> OrgUnit:
        sous_structure = self.sous_structure
        if sous_structure:
            return sous_structure
        else:
            return self.laboratoire

    @property
    def sous_structure(self) -> OrgUnit | None:
        from .roles import RoleType

        roles = self.roles
        roles = [r for r in roles if r.type == RoleType.MEMBRE.value]
        assert len(roles) in (0, 1)
        if roles:
            return roles[0].context
        else:
            return None

    @property
    def equipe(self) -> OrgUnit | None:
        from .unites import EQUIPE

        sous_structure = self.sous_structure
        if not sous_structure:
            return None
        if sous_structure.type == EQUIPE:
            return sous_structure
        parent = sous_structure.parent
        if parent.type == EQUIPE:
            return parent
        return None

    @property
    def departement(self) -> OrgUnit | None:
        from labster.domain.models.unites import DEPARTEMENT, EQUIPE

        sous_structure = self.sous_structure
        if not sous_structure:
            return None
        if sous_structure.type == DEPARTEMENT:
            return sous_structure
        if sous_structure.type == EQUIPE:
            parent = sous_structure.parent
            if parent.type == DEPARTEMENT:
                return parent
        return None


class AgentDgrttMixin:
    @property
    def bureau_dgrtt(self):
        """Mon bureau DGRTT."""
        return dgrtt_service.get_bureau_dgrtt(self)

    @property
    def perimetre_dgrtt(self):
        """Liste des labos auprès desquels l'agent intervient."""
        return dgrtt_service.get_perimetre_dgrtt(self)


class DirectionDgrttMixin:
    pass


class WorkflowActorMixin(RolesMixin):
    # Silence the typechecker
    laboratoire: OrgUnit | None

    @property
    def stucture_dont_je_suis_le_directeur(self) -> OrgUnit | None:
        return None

    @property
    def perimetre_dgrtt(self) -> set[OrgUnit]:
        return set()


class ProfileQuery(EntityQuery):
    def get_by_uid(self, uid: str) -> Profile:
        return self.filter(Profile.uid == uid).one()


class Profile(UserMixin, AgentDgrttMixin, RechercheMixin, WorkflowActorMixin, Entity):
    __tablename__ = "profile"
    __indexable__ = False
    query_class = ProfileQuery

    #: Unique id from LDAP (ex: "jdupont"), not the same as id (surrogate key)
    uid = Column(String, nullable=False, unique=True, index=True)

    # TODO: add 'nullable=False'
    active = Column(Boolean, default=True, server_default=text("TRUE"))

    nom = Column(Unicode, nullable=False)
    prenom = Column(Unicode, nullable=False)
    email = Column(String, nullable=False)

    adresse = Column(Unicode, default="")
    telephone = Column(Unicode, default="")

    laboratoire_id = Column(Integer, ForeignKey(OrgUnit.id))
    laboratoire = relationship(
        OrgUnit, foreign_keys=[laboratoire_id], backref="membres"
    )

    #: Membre de la gouvernance ?
    gouvernance = Column(Boolean)

    #: A vraiment les droits de la gouvernance
    gouvernance_vraiment = Column(Boolean)

    #: Membre de la DGRTT
    dgrtt = Column(Boolean)
    chef_du_bureau = Column(Unicode)

    #: LDAP stuff
    fonction_structurelle_principale = Column(Unicode)

    #: More LDAP stuff
    ldap_entry = Column(String)

    #: Infos récupérées au login (CAS)
    cas_entry = Column(String)

    date_derniere_notification_vue = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    date_last_login = Column(DateTime)

    #: FLUX_TENDU = 0
    #: DAILY = 1
    #: WEEKLY = 2
    preferences_notifications = Column(Integer, default=0)
    preferences_nb_jours_notifications = Column(Integer, default=0)

    @property
    def id(self):
        return self.uid

    @property
    def full_name(self) -> str:
        return f"{self.prenom} {self.nom}"

    @property
    def ldap_dict(self) -> dict[str, Any]:
        try:
            return json.loads(self.ldap_entry)
        except (ValueError, TypeError):
            return {}

    @property
    def cas_dict(self) -> dict[str, Any]:
        try:
            return json.loads(self.cas_entry)
        except (ValueError, TypeError):
            return {}

    def __repr__(self):
        return f"<Profile name={self.full_name} id={self.id}>"

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return False
        return self.uid == other.uid

    def __hash__(self):
        return hash(self.uid)

    def nb_notifications_non_vues(self) -> int:
        from .notifications import Notification

        return (
            Notification.query.filter(Notification.user == self)
            .filter(Notification.created_at > self.date_derniere_notification_vue)
            .count()
        )

    @property
    def is_directeur(self) -> bool:
        """Vrai si le profil est vraiment le directeur de la structure."""
        return "{15079}" in self.fonction_structurelle_principale
