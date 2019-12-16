from __future__ import annotations

from enum import Enum
from typing import Dict, Optional

from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure


class ContactType(Enum):
    CONTACT_ENTREPRISES = "Contact Entreprises"
    CONTACT_EUROPE = "Contact Europe"
    CONTACT_CONTRATS_PUBLICS = "Contact Contrats Publics"
    CONTACT_RH = "Contact RH"
    CONTACT_PI = "Contact PI"
    JURISTE_PI = "Juriste PI"
    CONTACT_DRV = "Contact DRV"
    CDP = "CDP"


class ContactService:
    def is_empty(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def set_contact(
        self, structure: Structure, contact_type: ContactType, user: Profile
    ):
        raise NotImplementedError

    def delete_contact(self, structure: Structure, contact_type: ContactType):
        raise NotImplementedError

    def get_contact(
        self, structure: Structure, contact_type: ContactType
    ) -> Optional[Profile]:
        raise NotImplementedError

    def get_mapping(self) -> Dict[Structure, Dict[ContactType, Profile]]:
        raise NotImplementedError

    def get_mapping_for(self, structure: Structure) -> Dict[ContactType, Profile]:
        raise NotImplementedError


#
# from typing import TYPE_CHECKING, Any, Optional, Set, Text
#
# import six
# from labster.extensions import db
# from flask import flash
# from sqlalchemy.orm import joinedload
#
# from labster.domain.services.constants import get_constant
#
# if TYPE_CHECKING:
#     from labster.domain.models.profiles import Profile
#     from labster.domain.models.unites import OrgUnit
#
#
# class BureauDgrtt(object):
#     def __init__(self, id):
#         self.id = id
#         self._nom = None
#
#     def __repr__(self):
#         return "<BureauDgrtt id={} nom={}>".format(self.id, self.nom)
#
#     @property
#     def nom(self):
#         if self._nom:
#             return self._nom
#         nom = get_constant("nom_bureaux_dgrtt." + self.id)
#         self._nom = nom
#         return nom
#
#     @staticmethod
#     def from_id(id):
#         for bureau in BUREAUX_DGRTT:
#             if bureau.id == id:
#                 return bureau
#         raise IndexError()
#
#
# BUREAUX_DGRTT = [
#     BureauDgrtt("ETT"),
#     BureauDgrtt("CFE"),
#     BureauDgrtt("CP"),
#     BureauDgrtt("CT"),
#     BureauDgrtt("PIJ"),
#     BureauDgrtt("PI2"),
#     BureauDgrtt("REF"),
# ]
#
#
# def bureaux():
#     return BUREAUX_DGRTT
#
#
# def get_membres():
#     """Retourne la liste des membres de la DR&I.
#     """
#     from labster.domain.models.profiles import Profile
#
#     return Profile.query.filter(Profile.dgrtt == True).order_by(Profile.nom).all()
#
#
# def est_referent(user):
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     return (
#         MappingDgrtt.query.filter_by(contact_dgrtt=user)
#         .filter_by(bureau_dgrtt="REF")
#         .count()
#         > 0
#     )
#
#
# def mapping():
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     result = {}
#     mappings = MappingDgrtt.query.options(
#         joinedload(MappingDgrtt.contact_dgrtt), joinedload(MappingDgrtt.ou_recherche)
#     ).all()
#
#     structures = {m.ou_recherche for m in mappings}
#     structures = sorted(list(structures))
#     for structure in structures:
#         line = []
#         for bureau in bureaux():
#             contacts = [
#                 m.contact_dgrtt
#                 for m in mappings
#                 if m.bureau_dgrtt == bureau.id and m.ou_recherche == structure
#             ]
#             if contacts:
#                 contact = contacts[0]
#             else:
#                 contact = None
#             line.append(contact)
#
#         result[structure] = line
#     return result
#
#
# def contacts_structure(structure):
#     """
#     Retourne un dictionnaire 'sigle bureau' -> contact pour une structure donnée.
#     """
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     result = {}
#     for bureau in bureaux():
#         mappings = (
#             MappingDgrtt.query.filter(MappingDgrtt.ou_recherche == structure)
#             .filter(MappingDgrtt.bureau_dgrtt == bureau.id)
#             .all()
#         )
#         assert len(mappings) in [0, 1]
#         if mappings:
#             result[bureau.id] = mappings[0].contact_dgrtt
#         else:
#             result[bureau.id] = None
#     return result
#
#
# def set_mapping(structure, bureau_id, contact):
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     mappings_to_delete = (
#         MappingDgrtt.query.filter(MappingDgrtt.ou_recherche == structure)
#         .filter(MappingDgrtt.bureau_dgrtt == bureau_id)
#         .all()
#     )
#     assert len(mappings_to_delete) in [0, 1]
#     for m in mappings_to_delete:
#         db.session.delete(m)
#
#     mapping = MappingDgrtt(
#         ou_recherche=structure, bureau_dgrtt=bureau_id, contact_dgrtt=contact
#     )
#     db.session.add(mapping)
#
#
# def get_referent(structure):
#     """Retourne le référent de la structure, ou None s'il n'y en a pas."""
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     mappings = (
#         MappingDgrtt.query.filter_by(bureau_dgrtt="REF")
#         .filter_by(ou_recherche=structure)
#         .all()
#     )
#     assert len(mappings) in (0, 1)
#
#     if len(mappings) == 0:
#         return None
#     return mappings[0].contact_dgrtt
#
#
# def labos_dont_je_suis_referent(user):
#     """Retourne la liste des structure dont l'utilisateur est référent."""
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     mappings = (
#         MappingDgrtt.query.filter_by(bureau_dgrtt="REF")
#         .filter_by(contact_dgrtt=user)
#         .all()
#     )
#
#     return {m.ou_recherche for m in mappings}
#
#
# def get_contact_dgrtt(structure, bureau_dgrtt):
#     # type: (OrgUnit, Text) -> Optional[Profile]
#     assert structure and bureau_dgrtt
#     assert isinstance(bureau_dgrtt, six.string_types)
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     mappings = (
#         MappingDgrtt.query.filter_by(ou_recherche=structure)
#         .filter_by(bureau_dgrtt=bureau_dgrtt)
#         .all()
#     )
#
#     assert len(mappings) in [0, 1]
#     if not mappings:
#         return None
#     return mappings[0].contact_dgrtt
#
#
# def get_membres_du_bureau_dgrtt(bureau_dgrtt):
#     """Retourne la liste des membres d'un bureau DR&I (DGRTT) donné."""
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     if not bureau_dgrtt:
#         return []
#
#     assert isinstance(bureau_dgrtt, BureauDgrtt)
#
#     mappings = MappingDgrtt.query.filter(
#         MappingDgrtt.bureau_dgrtt == bureau_dgrtt.id
#     ).all()
#
#     users = [m.contact_dgrtt for m in mappings]
#     users = sorted(users, key=lambda x: x.uid)
#     return users
#
#
# def get_bureau_dgrtt(user, check=False):
#     # type: (Profile, bool) -> Optional[BureauDgrtt]
#     """Retourne le bureau DR&I (DGRTT) d'appartenance d'un contact DGRTT.
#     """
#     if user.chef_du_bureau:
#         return BureauDgrtt.from_id(user.chef_du_bureau)
#
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     mappings = MappingDgrtt.query.filter(MappingDgrtt.contact_dgrtt == user).all()
#
#     bureau_ids = {m.bureau_dgrtt for m in mappings if m.bureau_dgrtt != "REF"}
#     if len(bureau_ids) > 1:
#         flash(
#             "L'utilisateur {} appartient à plus d'un bureau".format(user.full_name),
#             category="warning",
#         )
#         if check:
#             raise ValueError(
#                 "L'utilisateur {} appartient à plus d'un bureau".format(user.full_name)
#             )
#     if not bureau_ids:
#         return None
#     return BureauDgrtt.from_id(bureau_ids.pop())
#
#
# def get_perimetre_dgrtt(user):
#     # type: (Profile) -> Set[OrgUnit]
#     from labster.domain.models.mapping_dgrtt import MappingDgrtt
#
#     mappings = MappingDgrtt.query.filter(MappingDgrtt.contact_dgrtt == user).all()
#
#     return {m.ou_recherche for m in mappings}
#
#
# def check():
#     membres_dgrtt = get_membres()
#     for membre in membres_dgrtt:
#         perimetre = get_perimetre_dgrtt(membre)
#         for structure in perimetre:
#             contacts = contacts_structure(structure).values()
#             assert membre in contacts
#
#     from labster.domain.models.unites import OrgUnit
#
#     for structure in OrgUnit.query.all():
#         contacts = contacts_structure(structure)
#         for sigle_bureau, contact in contacts.items():
#             if contact and sigle_bureau != "REF":
#                 bureau = get_bureau_dgrtt(contact, check=True)
#                 assert bureau.id == sigle_bureau
#
#         referent = get_referent(structure)
#         if referent:
#             assert referent.has_role("référent")
#             assert structure in labos_dont_je_suis_referent(referent)
