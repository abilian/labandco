from __future__ import annotations

from typing import Collection, Dict, List, Optional, Tuple

import structlog
from attr import attrs
from ldif import LDIFRecordList
from tqdm import tqdm

from labster.di import injector
from labster.domain2.model.profile import Profile, ProfileRepository
from labster.domain2.model.structure import StructureRepository
from labster.domain2.services.roles import RoleService

logger = structlog.get_logger()

profile_repo = injector.get(ProfileRepository)
structure_repo = injector.get(StructureRepository)
role_service = injector.get(RoleService)


def get_ldif_file():
    fn = "annuaire/lab-co.ldif"
    return fn

    # # TODO later
    # files = glob.glob("annuaire/extraction-personnels.ldif")
    # files.sort()
    # if not files:
    #     logger.error("Error: not LDIF file found in annuaire/")
    #     sys.exit(-1)
    # ldif_file = files[-1]
    #
    # # Remove old files
    # for file_to_remove in files[0:-1]:
    #     logger.info(f"removing {file_to_remove}")
    #     os.unlink(file_to_remove)
    #
    # return ldif_file


def parse_ldif_file(ldif_file) -> List:
    logger.info(f"### Parsing LDIF file {ldif_file}")

    class LdifFileReader:
        def __init__(self, fd):
            self.fd = fd

        def __getattr__(self, name):
            class MethodProxy:
                def __init__(self, fd, name):
                    self.fd = fd
                    self.name = name

                def __call__(self, *args, **kw):
                    if self.name == "readline":
                        result = self.fd.readline()
                        if result.startswith("search:"):
                            return ""
                        else:
                            return result

                    result = getattr(self.fd, self.name)(*args, **kw)
                    return result

            return MethodProxy(self.fd, name)

    parser = LDIFRecordList(LdifFileReader(open(ldif_file, "r")))
    parser.parse()
    return parser.all_records


@attrs(auto_attribs=True)
class LdifRecord:
    dn: str
    raw: Dict[str, List[bytes]]

    @property
    def uid(self) -> Optional[str]:
        if "uid" not in self.raw:
            return None
        return self.raw["uid"][0].decode()

    @property
    def affectation(self) -> Optional[str]:
        affectations = self.raw.get("sorbonneUniversiteEmpAffectation", [])
        if not affectations:
            return None
        assert len(affectations) == 1
        return affectations[0].decode()

    @property
    def fonctions(self):
        affiliations = self.raw.get("eduPersonAffiliation", [])
        return [s.decode() for s in affiliations]

    def __getattr__(self, name):
        return self.raw.get(name, [b""])[0].decode()


def update_users_from_records(records: List[Tuple[str, Dict[str, List[bytes]]]]):
    structures = structure_repo.get_all()
    structure_dns = {s.dn for s in structures if s.dn}

    profiles = profile_repo.get_all()
    old_profile_uids = {p.uid for p in profiles}
    count0 = len(old_profile_uids)
    print(f"old total: {count0:d}")
    logger.info(f"old total: {count0:d}")

    new_profile_uids = set()
    for _dn, r in records:
        if "uid" not in r:
            continue
        uid = r["uid"][0].decode()
        new_profile_uids.add(uid)

    deleted_uids = old_profile_uids.difference(new_profile_uids)
    deactivate_users(deleted_uids)

    uids_to_profiles = {p.uid: p for p in profiles}

    for dn, r in tqdm(records):
        record = LdifRecord(dn, r)
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

        update_profile_from_record(profile, record, structure_dns)


def deactivate_users(deleted_uids):
    logger.info("To be deleted:", deleted_uids=deleted_uids)

    for uid in tqdm(deleted_uids):
        user = profile_repo.get_by_uid(uid)
        user.deactivate()


def update_profile_from_record(
    profile: Profile, record: LdifRecord, structure_dns: Collection[str]
):
    profile.nom = record.sn
    profile.prenom = record.givenName
    profile.telephone = record.telephoneNumber
    profile.adresse = record.postalAddress.replace("$", "\n")
    profile.login = record.supannAliasLogin

    affectation = record.affectation
    if not affectation or affectation not in structure_dns:
        if profile and profile.active:
            profile.active = False
            # TODO: log
        return

    if profile.affectation != affectation:
        # TODO: log
        print(profile.affectation, affectation)
        logger.info(f"Updating affectation for {record.uid} ({profile.name})")
        profile.affectation = affectation

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
