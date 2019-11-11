# from __future__ import annotations
#
# import glob
# import os
# import sys
#
# from labster.domain.models.profiles import Profile
# from labster.domain.models.roles import RoleType
# from labster.domain.models.unites import OrgUnit
# from labster.domain.services.roles import ungrant_role
# from labster.extensions import db
#
# from .parse import SynchronizingUserLDIFParser
#
#
# def sync_users():
#     print("## Synchronisation des utilisateurs")
#     ldif_file = get_ldif_file()
#     parse_ldif_file(ldif_file)
#     fix_structures()
#
#
# def get_ldif_file():
#     files = glob.glob("annuaire/DGRTT*.ldif")
#     files.sort()
#     if not files:
#         print("Error: not LDIF file found in annuaire/")
#         sys.exit(-1)
#     ldif_file = files[-1]
#
#     # Remove old files
#     for file_to_remove in files[0:-1]:
#         print(f"removing {file_to_remove}")
#         os.unlink(file_to_remove)
#
#     return ldif_file
#
#
# def parse_ldif_file(ldif_file):
#     print("### Parsing LDIF file {ldif_file}")
#     profile_uids = {p.uid: p for p in Profile.query.all()}
#     count0 = len(profile_uids)
#     print(f"old total: {count0:d}")
#     parser = SynchronizingUserLDIFParser(open(ldif_file, "rb"))
#     parser.parse()
#     users = parser.users
#     print(f"from ldif: {len(users):d}")
#     deactivated = 0
#     reactivated = 0
#     for p in profile_uids.values():
#         if p.active and p.uid not in users:
#             p.active = False
#             deactivated += 1
#         if not p.active and p.uid in users:
#             p.active = True
#             reactivated += 1
#     db.session.flush()
#     print(f"deactivated: {deactivated}")
#     print(f"reactivated: {reactivated}")
#     added = 0
#     for uid, u in users.items():
#         if uid not in profile_uids:
#             p = Profile(**u)
#             p.set_default_roles()
#             db.session.add(p)
#             added += 1
#
#         else:
#             p = Profile.query.get_by_uid(uid)
#             for k, v in u.items():
#                 if getattr(p, k, None) != v:
#                     setattr(p, k, v)
#     db.session.flush()
#     print(f"added: {added}")
#     user_count = Profile.query.count()
#     print(f"new total: {user_count}")
#     db.session.commit()
#
#
# def fix_structures():
#     print("### Fix des sous-structures")
#     for profile in Profile.query.all():
#         structure = profile.structure  # type: OrgUnit
#         labo = profile.laboratoire
#
#         if not labo or not structure:
#             continue
#
#         if labo == structure:
#             continue
#
#         if labo in structure.parents:
#             continue
#
#         print("Fixing labo for:", profile.full_name)
#         ungrant_role(profile, RoleType.MEMBRE, structure)
#
#     db.session.commit()
from __future__ import annotations
