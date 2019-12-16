from __future__ import annotations

import re
from io import BytesIO
from typing import Any, Collection, Dict, List, Optional, Tuple

import structlog
from attr import attrs
from ldif import LDIFParser
from tqdm import tqdm

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.ldap.constants import ADMINS_DN, get_parent_dn

logger = structlog.get_logger()

profile_repo = injector.get(ProfileRepository)
structure_repo = injector.get(StructureRepository)


def parse_ldif_file(ldif_file: str) -> List[Tuple[str, Dict[str, Any]]]:
    logger.info(f"### Parsing LDIF file {ldif_file}")

    orig_ldif_fd = open(ldif_file, "rb")
    ldif_fd = BytesIO()
    for line in orig_ldif_fd.readlines():
        if line.startswith(b"# search result"):
            break
        ldif_fd.write(line)

    ldif_fd.seek(0)

    parser = LDIFParser(ldif_fd)
    return list(parser.parse())


@attrs(auto_attribs=True)
class LdifRecord:
    raw: Dict[str, List[str]]

    def __getattr__(self, name):
        return self.raw.get(name, [""])[0]

    @property
    def uid(self) -> Optional[str]:
        if "uid" not in self.raw:
            return None
        return self.raw["uid"][0]

    @property
    def affectation(self) -> Optional[str]:
        affectations = self.raw.get("sorbonneUniversiteEmpAffectation")
        if not affectations:
            return None

        # assert len(affectations) == 1
        affectation = affectations[0]

        if affectation in ADMINS_DN:
            affectation = get_parent_dn(affectation)

        return affectation

    @property
    def fonctions(self):
        return self.raw.get("eduPersonAffiliation", [])

    @property
    def address(self):
        adresse = self.raw.get("postalAddress", [""])[0]
        adresse = adresse.replace("$", "\n")
        adresse = re.sub("\n\n+", "\n\n", adresse)
        adresse = adresse.strip()
        return adresse


def update_users_from_records(records: List[Tuple[str, Dict[str, List[str]]]]):
    profiles = profile_repo.get_all()
    old_profile_uids = {p.uid for p in profiles if p.uid}
    count0 = len(old_profile_uids)
    print(f"old total: {count0:d}")
    logger.info(f"old total: {count0:d}")

    new_profile_uids = set()
    for _dn, r in records:
        if "uid" not in r:
            continue
        uid = r["uid"][0]
        new_profile_uids.add(uid)

    deleted_uids = old_profile_uids.difference(new_profile_uids)
    deactivate_users(deleted_uids)

    uids_to_profiles = {p.uid: p for p in profiles}

    for _dn, r in tqdm(records):
        record = LdifRecord(r)
        if not record.uid:
            continue
        uid = record.uid
        if not uid:
            continue
        if uid in uids_to_profiles:
            profile = uids_to_profiles[uid]
        else:
            profile = Profile(uid=uid)
            profile_repo.put(profile)

        update_profile_from_record(profile, record)


def deactivate_users(deleted_uids):
    logger.info("To be deactivated:", deleted_uids=deleted_uids)

    for uid in tqdm(deleted_uids):
        user = profile_repo.get_by_uid(uid)
        user.deactivate()


def update_profile_from_record(profile: Profile, record: LdifRecord):
    profile.nom = record.sn
    profile.prenom = record.givenName
    profile.uid = record.uid
    profile.email = record.mail
    profile.telephone = record.telephoneNumber
    profile.adresse = record.address
    profile.login = record.supannAliasLogin
    profile.adresse = record.adresse

    affectation = record.affectation
    structure_d_affectation = None
    if affectation:
        structure_d_affectation = structure_repo.get_by_dn(affectation)

    if not structure_d_affectation:
        if profile and profile.active:
            profile.affectation = ""
            profile.deactivate()
            profile.active = False
            # TODO: log
        return

    if not profile.active:
        profile.activate()

    if profile.affectation != affectation:
        # TODO: log
        # print(profile.affectation, affectation)
        # logger.info(f"Updating affectation for {record.uid} ({profile.name})")
        profile.affectation = affectation or ""

    fonctions = list(record.fonctions)
    if set(profile.fonctions) != set(fonctions):
        profile.fonctions = fonctions

    # parser = SynchronizingUserLDIFParser(open(ldif_file, "rb"))
    # parser.parse()
    # users = parser.users
    # print(f"from ldif: {len(users):d}")
    # deactivated = 0
    # reactivated = 0
    # for p in profile_uids.values():
    #     if p.active and p.uid not in users:
    #         p.active = False
    #         deactivated += 1
    #     if not p.active and p.uid in users:
    #         p.active = True
    #         reactivated += 1
    # db.session.flush()
    # print(f"deactivated: {deactivated}")
    # print(f"reactivated: {reactivated}")
    # added = 0
    # for uid, u in users.items():
    #     if uid not in profile_uids:
    #         p = Profile(**u)
    #         p.set_default_roles()
    #         db.session.add(p)
    #         added += 1
    #
    #     else:
    #         p = Profile.query.get_by_uid(uid)
    #         for k, v in u.items():
    #             if getattr(p, k, None) != v:
    #                 setattr(p, k, v)
    # db.session.flush()
    # print(f"added: {added}")
    # user_count = Profile.query.count()
    # print(f"new total: {user_count}")
    # db.session.commit()
