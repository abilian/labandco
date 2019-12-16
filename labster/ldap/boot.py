from __future__ import annotations

from typing import Dict, Optional

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain.models.profiles import Profile as OldProfile

from .ldif import LdifRecord, parse_ldif_file, update_profile_from_record

structure_repo = injector.get(StructureRepository)
profile_repo = injector.get(ProfileRepository)


def import_from_ldap():
    records = parse_ldif_file("annuaire/extraction-personnels.ldif")

    count = 0
    for _dn, entry in records:
        profile = make_profile(entry)
        if not profile:
            continue

        login = profile.login
        old_profile = OldProfile.query.filter_by(uid=login).first()
        if old_profile and old_profile.active:
            profile.old_uid = old_profile.uid
            profile.old_id = old_profile.id

        profile_repo.put(profile)
        count += 1

    print(f"{count} profiles imported")


def make_profile(entry: Dict) -> Optional[Profile]:
    record = LdifRecord(entry)
    if not record.mail:
        return None
    affectation = record.affectation
    if not affectation:
        return None
    structure_d_affectation = structure_repo.get_by_dn(affectation)
    if not structure_d_affectation:
        return None

    profile = Profile()
    update_profile_from_record(profile, record)
    return profile
