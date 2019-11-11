# """"""
# from __future__ import annotations
#
# import json
# import re
# import time
# from typing import Dict, List
#
# from ldif import LDIFParser
#
# from labster.domain.models.profiles import Profile
# from labster.domain.models.unites import LABORATOIRE, OrgUnit
# from labster.extensions import db
#
# DN_DGRTT = "ou=0107,ou=SG,ou=UPMC,ou=Affectations,dc=upmc,dc=fr"
# DN_PRESIDENCE = "ou=0101,ou=DUPMC,ou=UPMC,ou=Affectations,dc=upmc,dc=fr"
#
#
# class MyLDIFParser(LDIFParser):
#     def __init__(self, input):
#         LDIFParser.__init__(self, input)
#         self.count = 0
#         self.t0 = time.time()
#         self.labos = OrgUnit.query.filter_by_type(LABORATOIRE).all()
#
#     def handle(self, dn: str, entry_bytes: Dict[str, List[bytes]]) -> None:
#         entry: Dict[str, List[str]] = {
#             k: [x.decode("utf8") for x in v] for k, v in entry_bytes.items()
#         }
#
#         uid = entry["uid"][0]
#
#         default_email = f"{uid}@upmc.fr"
#         email = (entry.get("mail") or [default_email])[0]
#         nom = entry["sn"][0]
#         prenom = entry["givenName"][0]
#
#         telephone = entry.get("telephoneNumber", [""])[0]
#         adresse = entry.get("postalAddress", [""])[0]
#
#         adresse = adresse.replace("$", "\n")
#         adresse = re.sub("\n\n+", "\n\n", adresse)
#         adresse = adresse.strip()
#
#         affectations = entry.get("supannAffectation", [])
#         if not affectations:
#             return
#         laboratoire = self.labo_d_affectaction(affectations)
#
#         dgrtt = affectations[0].endswith(DN_DGRTT)
#
#         if not (laboratoire or dgrtt):
#             return
#
#         profile = Profile(
#             uid=uid,
#             email=email,
#             nom=nom,
#             prenom=prenom,
#             adresse=adresse,
#             telephone=telephone,
#             laboratoire=laboratoire,
#         )
#
#         db.session.add(profile)
#
#         self.count += 1
#         if self.count % 100 == 0:
#             t1 = time.time()
#             print(self.count, t1 - self.t0)
#             self.t0 = t1
#
#     def labo_d_affectaction(self, affectations):
#         for affectation in affectations:
#             for labo in self.labos:
#                 if affectation.endswith(labo.dn + ",dc=upmc,dc=fr"):
#                     return labo
#         return None
#
#
# class SynchronizingUserLDIFParser(LDIFParser):
#     def __init__(self, input):
#         LDIFParser.__init__(self, input)
#         self.users = {}
#         self.uids_to_delete = set()
#         self.labos = OrgUnit.query.filter_by_type(LABORATOIRE).all()
#
#     def handle(self, dn: str, entry_bytes: Dict[str, List[bytes]]) -> None:
#         entry: Dict[str, List[str]] = {
#             k: [x.decode("utf8") for x in v] for k, v in entry_bytes.items()
#         }
#
#         uid = entry["uid"][0]
#
#         default_email = f"{uid}@upmc.fr"
#         email = (entry.get("mail") or [default_email])[0]
#         nom = entry["sn"][0]
#         prenom = entry["givenName"][0]
#
#         telephone = entry.get("telephoneNumber", [""])[0]
#
#         adresse = self.adresse(entry)
#         gouvernance = self.gouvernance(entry)
#
#         affectations = entry.get("affectationPrincipale", [])
#         if not affectations:
#             return
#         assert len(affectations) == 1
#         affectation = affectations[0]
#         laboratoire = self.labo_d_affectaction(affectation)
#
#         fsp = entry.get("fonctionStructurellePrincipale", [""])[0]
#
#         dgrtt = affectation.endswith(
#             "ou=0107,ou=SG,ou=UPMC,ou=Affectations,dc=upmc,dc=fr"
#         )
#
#         if not (laboratoire or dgrtt or gouvernance or fsp):
#             self.uids_to_delete.add(uid)
#             return
#
#         user = {
#             "uid": uid,
#             "email": email,
#             "nom": nom,
#             "prenom": prenom,
#             "adresse": adresse,
#             "telephone": telephone,
#             "laboratoire": laboratoire,
#             "dgrtt": dgrtt,
#             "gouvernance": gouvernance,
#             "fonction_structurelle_principale": fsp,
#             "ldap_entry": json.dumps(entry),
#         }
#
#         self.users[uid] = user
#
#     @staticmethod
#     def adresse(entry):
#         adresse = entry.get("postalAddress", [""])[0]
#         adresse = adresse.replace("$", "\n")
#         adresse = re.sub("\n\n+", "\n\n", adresse)
#         adresse = adresse.strip()
#         return adresse
#
#     def gouvernance(self, entry):
#         gouvernance = False
#         fonctions_structurelles = entry.get("fonctionStructurellePrincipale", [])
#         if fonctions_structurelles:
#             assert len(fonctions_structurelles) == 1
#             fonction_structurelle = fonctions_structurelles[0]
#             start = fonction_structurelle.index("}") + 1
#             fonction_structurelle = fonction_structurelle[start:]
#             if fonction_structurelle in ["Vice-président", "Président d'université"]:
#                 gouvernance = True
#
#         affectations = entry.get("affectationPrincipale", [])
#         if affectations:
#             assert len(affectations) == 1
#             affectation = affectations[0]
#             if affectation == DN_PRESIDENCE:
#                 gouvernance = True
#
#         return gouvernance
#
#     def labo_d_affectaction(self, affectation):
#         for labo in self.labos:
#             if affectation.endswith(labo.dn + ",dc=upmc,dc=fr"):
#                 return labo
#         return None
from __future__ import annotations
