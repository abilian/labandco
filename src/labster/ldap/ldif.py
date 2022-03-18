from __future__ import annotations

import re
from io import BytesIO
from typing import Any

import structlog
from attr import attrs
from flask_sqlalchemy import SQLAlchemy
from ldif import LDIFParser
from tqdm import tqdm

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import Structure, StructureRepository
from labster.ldap.constants import ADMINS_DN, PRESIDENCE_DN, SU_DN, \
    get_parent_dn

logger = structlog.get_logger()

profile_repo = injector.get(ProfileRepository)
structure_repo = injector.get(StructureRepository)
db = injector.get(SQLAlchemy)


def parse_ldif_file(ldif_file: str) -> list[tuple[str, dict[str, Any]]]:
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
    raw: dict[str, list[str]]

    def __getattr__(self, name):
        return self.raw.get(name, [""])[0]

    @property
    def uid(self) -> str | None:
        if "uid" not in self.raw:
            return None
        return self.raw["uid"][0]

    @property
    def affectation(self) -> str | None:
        structure_affectaction = self._get_structure_d_affectation()
        if not structure_affectaction:
            return None

        affectation = structure_affectaction.dn
        if affectation in ADMINS_DN:
            affectation = get_parent_dn(affectation)

        if affectation == PRESIDENCE_DN:
            affectation = SU_DN

        return affectation

    def _get_structure_d_affectation(self) -> Structure | None:
        structure_d_affectation = None

        affectation_principale = self.supannEntiteAffectationPrincipale
        if affectation_principale:
            structure_d_affectation = (
                db.session.query(Structure)
                .filter(Structure.supann_code_entite == affectation_principale)
                .first()
            )
            if structure_d_affectation:
                return structure_d_affectation

        # Old LDIF format
        affectation = self.sorbonneUniversiteEmpAffectation
        if affectation:
            structure_d_affectation = (
                db.session.query(Structure).filter(Structure.dn == affectation).first()
            )
            if structure_d_affectation:
                return structure_d_affectation

        return None

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


def update_users_from_records(records: list[tuple[str, dict[str, list[str]]]]):
    profiles = profile_repo.get_all()
    old_profile_uids = {
        profile.uid for profile in profiles if profile.uid and profile.active
    }
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

    print("Updating profiles from LDIF dump")
    for _dn, r in tqdm(records, disable=None):
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

    for uid in tqdm(deleted_uids, disable=None):
        user = profile_repo.get_by_uid(uid)
        user.deactivate()


def update_profile_from_record(profile: Profile, record: LdifRecord):
    assert profile

    profile.nom = record.sn
    profile.prenom = record.givenName
    profile.uid = record.uid
    profile.email = record.mail
    profile.telephone = record.telephoneNumber
    profile.adresse = record.address
    profile.login = record.supannAliasLogin
    profile.adresse = record.adresse

    affectation = record.affectation

    if not affectation:
        if profile.active:
            profile.affectation = ""
            profile.deactivate()
        return

    if not profile.active:
        profile.activate()

    if profile.affectation != affectation:
        profile.affectation = affectation

    fonctions = list(record.fonctions)
    if set(profile.fonctions) != set(fonctions):
        profile.fonctions = fonctions
