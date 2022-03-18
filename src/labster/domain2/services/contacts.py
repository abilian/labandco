from __future__ import annotations

from enum import Enum

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
    ) -> Profile | None:
        raise NotImplementedError

    def get_mapping(self) -> dict[Structure, dict[ContactType, Profile]]:
        raise NotImplementedError

    def get_mapping_for(self, structure: Structure) -> dict[ContactType, Profile]:
        raise NotImplementedError
