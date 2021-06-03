from __future__ import annotations

from sqlalchemy.orm import scoped_session

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.model.type_structure import UN
from labster.domain2.services.contacts import ContactService, ContactType
from labster.domain2.services.roles import RoleService

profile_repo = injector.get(ProfileRepository)
structure_repo = injector.get(StructureRepository)
role_service = injector.get(RoleService)
contact_service = injector.get(ContactService)


def test_contact_service(db_session: scoped_session):
    # # TODO: remove
    # profile_repo.clear()
    # structure_repo.clear()
    # contact_service.clear()

    assert profile_repo.is_empty()
    assert structure_repo.is_empty()
    assert contact_service.is_empty()

    user = Profile()
    profile_repo.put(user)

    universite = Structure(nom="SU", type_name=UN.name)
    structure_repo.put(universite)

    # Actual test
    contact_service.set_contact(universite, ContactType.CDP, user)
    assert contact_service.get_contact(universite, ContactType.CDP) == user

    map = contact_service.get_mapping()
    map1 = map[universite]
    assert map1[ContactType.CDP] == user

    contact_service.delete_contact(universite, ContactType.CDP)
    assert contact_service.get_contact(universite, ContactType.CDP) == None

    map = contact_service.get_mapping()
    assert universite not in map

    # Cleanup
    profile_repo.clear()
    structure_repo.clear()
    contact_service.clear()
