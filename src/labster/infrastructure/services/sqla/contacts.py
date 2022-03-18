from __future__ import annotations

import uuid
from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import mapper, relationship

from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.services.contacts import ContactService, ContactType


def new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class Contact:
    id: str
    structure_id: str
    user_id: str
    contact_type_name: str


def make_mapper(metadata):
    table = Table(
        "v3_contacts",
        metadata,
        #
        Column("id", String(36), primary_key=True),
        Column("user_id", String(36), ForeignKey(Profile.id)),
        Column("structure_id", String(36), ForeignKey(Structure.id)),
        Column("contact_type_name", String(64), index=True, nullable=False),
    )

    mapper(
        Contact,
        table,
        properties={
            "structure": relationship(Structure),
            "user": relationship(Profile),
        },
    )


class SqlaContactService(ContactService):
    profile_repo = ProfileRepository
    structure_repo = StructureRepository

    @inject
    def __init__(
        self,
        db: SQLAlchemy,
        profile_repo: ProfileRepository,
        structure_repo: StructureRepository,
    ):
        self.profile_repo = profile_repo
        self.structure_repo = structure_repo
        self.db = db
        self.session = self.db.session
        make_mapper(self.db.metadata)

    def query(self):
        return self.session.query(Contact)

    def is_empty(self):
        return self.query().count() == 0

    def clear(self):
        self.query().delete()
        self.session.flush()

    def get_contact(
        self, structure: Structure, contact_type: ContactType
    ) -> Profile | None:

        assert isinstance(structure, Structure)
        assert isinstance(contact_type, ContactType)

        query = (
            self.query()
            .filter(Contact.structure_id == structure.id)
            .filter(Contact.contact_type_name == contact_type.name)
        )

        contact: Contact | None = query.first()
        if contact:
            return contact.user
        else:
            return None

    def set_contact(
        self, structure: Structure, contact_type: ContactType, user: Profile
    ):
        assert isinstance(structure, Structure)
        assert isinstance(contact_type, ContactType)
        assert isinstance(user, Profile)

        if self.get_contact(structure, contact_type) == user:
            return

        self.delete_contact(structure, contact_type)

        contact = Contact(new_id(), structure.id, user.id, contact_type.name)
        self.db.session.add(contact)
        self.db.session.flush()

    def delete_contact(self, structure: Structure, contact_type: ContactType):
        assert isinstance(structure, Structure)
        assert isinstance(contact_type, ContactType)

        query = (
            self.query()
            .filter(Contact.structure_id == structure.id)
            .filter(Contact.contact_type_name == contact_type.name)
        )

        contact: Contact | None = query.first()
        if contact:
            self.db.session.delete(contact)
            self.db.session.flush()

    def get_mapping_for(self, structure: Structure) -> dict[ContactType, Profile]:
        assert isinstance(structure, Structure)

        query = self.query().filter(Contact.structure_id == structure.id)

        contacts = query.all()
        return {ContactType[c.contact_type_name]: c.user for c in contacts}

    def get_mapping(self) -> dict[Structure, dict[ContactType, Profile]]:
        # TODO: optimize
        query = self.query()
        structures = {c.structure for c in query.all()}

        result = {
            structure: self.get_mapping_for(structure) for structure in structures
        }
        return result

        # result = {}
        # contact_types = list(ContactType)
        #
        # contacts = self.query().all()
        # edges = {
        #     (c.structure_id, ContactType[c.contact_type_name], c.user_id)
        #     for c in contacts
        # }
        #
        # structure_ids = {edge[0] for edge in edges}
        #
        # structures = [
        #     self.structure_repo.get_by_id(StructureId(structure_id))
        #     for structure_id in structure_ids
        # ]
        # structures.sort(key=lambda x: x.name)
        #
        # for structure in structures:
        #     d = {key: None for key in contact_types}
        #     for edge in edges:
        #         if edge[0] == structure.id:
        #             contact_type = edge[1]
        #             user = self.profile_repo.get_by_id(ProfileId(edge[2]))
        #             d[contact_type] = user
        #     result[structure] = d
        #
        # return result
