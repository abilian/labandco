# """"""
# from __future__ import annotations
#
# import csv
# import glob
#
# from sqlalchemy.orm.exc import NoResultFound
# from unidecode import unidecode
#
# from labster.domain.models.financeurs import Financeur
# from labster.domain.models.profiles import Profile
# from labster.domain.models.roles import Role, RoleType
# from labster.domain.models.unites import LABORATOIRE, POLE_DE_RECHERCHE, UFR, \
#     OrgUnit
# from labster.extensions import db
# from labster.ldap.parse import MyLDIFParser
#
# # BUREAUX_DGRTT = [
# #     'ETT', 'Europe', 'CPNL', 'RH', 'AIPI 1', 'AIPI 2', 'Com', 'Finance 1',
# #     'Finance 2', 'Finance 3', 'Moyens'
# # ]
# POLES = [
#     "1 - Modélisation et ingénierie",
#     "2 - Energie, matière et univers",
#     "3 - Terre vivante et environnement",
#     "4 - Vie et santé",
# ]
#
# UFR2POLE = {
#     "UFR Terre, Environnement, Biodiversite": 2,
#     "UFR Chimie": 1,
#     "UFR Faculte De Mathematiques": 0,
#     "UFR Ingenierie": 0,
#     "UFR Sciences De La Vie": 3,
#     "UFR Faculte De Medecine Pierre Et Marie Curie": 3,
#     "UFR Faculte De Physique": 1,
#     # Cas particulier des stations marines
#     "Observatoire Oceanologique De Banyuls": 2,
#     "Observatoire Oceanologique De Villefranche": 2,
#     "Station Biologique De Roscoff": 2,
# }
#
#
# class StructureLoader:
#     def __init__(self):
#         self.ufrs = set()
#         self.dns = set()
#
#     def load_ufrs(self):
#         self.parse_dump_ldap(self.create_ufr)
#
#     def load_labos(self):
#         self.parse_dump_infolab()
#
#     def parse_dump_infolab(self):
#         with open("boot/structures_recherche.csv", "rb") as fd:
#             reader = csv.reader(fd, delimiter=b";")
#
#             # Skip column names
#             reader.next()
#
#             for line in reader:
#                 self.parse_dump_infolab_line(line)
#
#     @staticmethod
#     def parse_dump_infolab_line(line):
#         dn = line[0]
#         nom_labo = str(line[3], "utf8")
#         sigle_labo = str(line[4], "utf8")
#         pole_num = int(line[5])
#
#         if "," not in dn:
#             return
#         if dn == "ou=67870,ou=967,ou=UPMC,ou=Affectations":
#             print(f"Skipping duplicate DN: {dn}")
#             return
#
#         ufr_dn = ",".join(dn.split(",")[1:])
#         try:
#             ufr = OrgUnit.query.get_by_dn(ufr_dn)
#             parent = ufr
#         except NoResultFound:
#             nom_du_pole = POLES[pole_num - 1]
#             pole = OrgUnit.query.get_by_nom(nom_du_pole)
#             parent = pole
#
#         data = {
#             "type": LABORATOIRE,
#             "dn": dn,
#             "nom": nom_labo,
#             "sigle": sigle_labo,
#             "parent": parent,
#         }
#
#         labo = OrgUnit(**data)
#         db.session.add(labo)
#
#     def parse_dump_ldap(self, callback):
#         files = glob.glob("annuaire/StructuresDGRTT*.csv")
#         files.sort()
#         filename = files[-1]
#
#         with open(filename, "rb") as fd:
#             reader = csv.reader(fd, delimiter=b";")
#
#             for line in reader:
#                 dn = line[0]
#                 nom = str(line[2], "latin1")
#                 path = list(reversed([s[3:] for s in dn.split(",")]))
#                 if len(path) < 3 or path[0] != "Affectations" or path[1] != "UPMC":
#                     continue
#
#                 callback(path, dn, nom)
#
#     def create_ufr(self, path, dn, nom):
#         if len(path) != 3:
#             return
#         nom = nom.replace("Ufr", "UFR")
#         print(nom, nom in UFR2POLE)
#         if nom not in UFR2POLE:
#             return
#
#         nom_du_pole = POLES[UFR2POLE[nom]]
#         pole = OrgUnit.query.get_by_nom(nom_du_pole)
#         ufr = OrgUnit(dn=dn, nom=nom, type=UFR, parent=pole)
#         self.ufrs.add(ufr)
#         db.session.add(ufr)
#
#
# def createpoles():
#     print("## Création des pôles de recherche")
#     for nom in POLES:
#         pole = OrgUnit(type=POLE_DE_RECHERCHE, nom=nom)
#         db.session.add(pole)
#     db.session.commit()
#
#     count = OrgUnit.query.filter_by_type(POLE_DE_RECHERCHE).count()
#     print(f"{count} pôles de recherche créés")
#
#
# # def createbureauxdgrtt():
# #     print(u"## Création des bureaux DGRTT")
# #     for nom in BUREAUX_DGRTT:
# #         bureau = OrgUnit(type=BUREAU_DGRTT, nom=nom)
# #         db.session.add(bureau)
# #     db.session.commit()
# #
# #     count = OrgUnit.query.filter_by_type(BUREAU_DGRTT).count()
# #     print("{} bureaux dgrtt créés".format(count))
#
#
# def loadusers(ldif_file):
#     """Load the users from the LDAP dump."""
#     print("## Chargement des utilisateurs")
#     Profile.query.delete()
#     parser = MyLDIFParser(open(ldif_file, "rb"))
#     parser.parse()
#     db.session.commit()
#
#     user_count = Profile.query.count()
#     print(f"{user_count} users created")
#
#
# def loadstructure():
#     """Load the structure from the various dumps."""
#     print("## Chargement de la structure")
#
#     # createbureauxdgrtt()
#     createpoles()
#
#     db.session.commit()
#     validatedb()
#
#     print("## Chargement des UFRs")
#     loader = StructureLoader()
#
#     loader.load_ufrs()
#     db.session.commit()
#     validatedb()
#
#     print("## Chargement des labos")
#     loader.load_labos()
#     db.session.commit()
#     validatedb()
#
#     ufr_count = OrgUnit.query.ufrs_count()
#     labos_count = OrgUnit.query.labos_count()
#     print(f"{ufr_count} UFR créées")
#     print(f"{labos_count} Structures créées")
#
#
# def loadfinanceurs():
#     print("## Chargement des financeurs")
#
#     Financeur.query.delete()
#     db.session.commit()
#
#     with open("boot/financeurs.csv", "rb") as fd:
#         reader = csv.reader(fd, delimiter=b";")
#         reader.next()
#         for line in reader:
#             data = {
#                 "nom": str(line[0], "utf8"),
#                 "sigle": str(line[1], "utf8"),
#                 "type": str(line[2], "utf8"),
#                 "sous_type": str(line[3], "utf8"),
#                 "classe": str(line[4], "utf8"),
#                 "pays": str(line[5], "utf8"),
#             }
#             financeur = Financeur(**data)
#             db.session.add(financeur)
#     db.session.commit()
#
#
# # def loadmappingdgrtt():
# #     print(u"## Chargement du mapping DGRTT")
# #
# #     MappingDgrtt.query.delete()
# #     db.session.commit()
# #
# #     def add_entry(contact_uid, bureau_sigle, ou_sigle):
# #         print(contact_uid, bureau_sigle, ou_sigle)
# #         try:
# #             contact = Profile.query.get_by_uid(contact_uid)
# #         except:
# #             print(u"!!! Impossible de trouver l'utilisateur: {}".format(
# #                 contact_uid))
# #             return
# #
# #         try:
# #             ou_recherche = OrgUnit.query.filter(OrgUnit.sigle == ou_sigle).one()
# #         except:
# #             print("Org w/ sigle = {} introuvable".format(ou_sigle))
# #             return
# #
# #         bureau_dgrtt = OrgUnit.query.get_by_nom(bureau_sigle)
# #         mapping_dgrtt = MappingDgrtt(contact_dgrtt=contact,
# #                                      ou_recherche=ou_recherche,
# #                                      bureau_dgrtt=bureau_dgrtt)
# #         db.session.add(mapping_dgrtt)
# #
# #     with open("boot/mapping_dgrtt.csv", "rb") as fd:
# #         reader = csv.reader(fd, delimiter=b';')
# #         reader.next()
# #         for line in reader:
# #             ou_recherche_sigle = text_type(line[0], 'utf8')
# #
# #             # ;ETT;Europe;CPNL;RH;AIPI;;Com;Finance 1;Finance 2;Finance 3;Moyens;^M
# #             for i, bureau_sigle in enumerate(
# #                 ['ETT', 'Europe', 'CPNL', 'RH', 'AIPI 1', 'AIPI 2', 'Com',
# #                  'Finance 1', 'Finance 2', 'Finance 3', 'Moyens']):
# #                 contact_uid = line[i + 1].strip()
# #                 if not contact_uid:
# #                     continue
# #                 add_entry(contact_uid, bureau_sigle, ou_recherche_sigle)
# #
# #     db.session.commit()
#
# # def loaddirecteurs():
# #     print(u"## Chargement des directeurs de labo")
# #
# #     Role.query.delete()
# #     db.session.commit()
# #
# #     with open("boot/structures_recherche.csv", "rb") as fd:
# #         reader = csv.reader(fd, delimiter=b';')
# #
# #         # Skip column names
# #         reader.next()
# #
# #         def quasi_equals(s1, s2):
# #             s1 = unidecode(s1.lower()).replace("-", " ")
# #             s2 = unidecode(s2.lower()).replace("-", " ")
# #             return s1 == s2
# #
# #         profiles = Profile.query.all()
# #
# #         for line in reader:
# #             dn = line[0]
# #             nom_labo = text_type(line[3], 'utf8').strip()
# #             prenom_directeur = text_type(line[9], 'utf8').strip()
# #             nom_directeur = text_type(line[10], 'utf8').strip()
# #
# #             if ',' not in dn:
# #                 continue
# #             if dn == 'ou=67870,ou=967,ou=UPMC,ou=Affectations':
# #                 continue
# #
# #             labo = OrgUnit.query.get_by_dn(dn)
# #
# #             directeur = None
# #
# #             for p in profiles:
# #                 if quasi_equals(p.nom, nom_directeur) and quasi_equals(
# #                         p.prenom, prenom_directeur):
# #                     directeur = p
# #                     break
# #             if not directeur:
# #                 print(
# #                     "Impossible de trouver le directeur ({} {}) du labo {}.".format(
# #                         prenom_directeur, nom_directeur, nom_labo))
# #                 continue
# #
# #             data = {'type': RoleType.DIRECTION,
# #                     'profile': directeur,
# #                     'context': labo,}
# #             role = Role(**data)
# #             db.session.add(role)
# #
# #     db.session.commit()
#
#
# def init_roles_direction():
#     roles = Role.query.filter_by(type=RoleType.DIRECTION.value).all()
#     for role in roles:
#         db.session.delete(role)
#
#     print("## Chargement des directeurs de labo")
#
#     with open("boot/structures_recherche.csv", "rb") as fd:
#         reader = csv.reader(fd, delimiter=b";")
#
#         # Skip column names
#         reader.next()
#
#         def quasi_equals(s1, s2):
#             s1 = unidecode(s1.lower()).replace("-", " ")
#             s2 = unidecode(s2.lower()).replace("-", " ")
#             return s1 == s2
#
#         profiles = Profile.query.all()
#
#         for line in reader:
#             dn = line[0]
#             nom_labo = str(line[3], "utf8").strip()
#             prenom_directeur = str(line[9], "utf8").strip()
#             nom_directeur = str(line[10], "utf8").strip()
#
#             if "," not in dn:
#                 continue
#             if dn == "ou=67870,ou=967,ou=UPMC,ou=Affectations":
#                 continue
#
#             labo = OrgUnit.query.get_by_dn(dn)
#
#             directeur = None
#
#             for p in profiles:
#                 if quasi_equals(p.nom, nom_directeur) and quasi_equals(
#                     p.prenom, prenom_directeur
#                 ):
#                     directeur = p
#                     break
#             if not directeur:
#                 print(
#                     "Impossible de trouver le directeur ({} {}) du labo {}.".format(
#                         prenom_directeur, nom_directeur, nom_labo
#                     )
#                 )
#                 continue
#
#             data = {
#                 "type": RoleType.DIRECTION.value,
#                 "profile": directeur,
#                 "context": labo,
#             }
#             # print(
#             #     "Ajout de {} comme directeur du labo {}"
#             #         .format(directeur.full_name, labo.nom).encode('utf8'))
#             role = Role(**data)
#             db.session.add(role)
#
#
# def validatedb():
#     def validate_org_units():
#         orgunits = OrgUnit.query.all()
#         for ou in orgunits:
#             # print("Checking {}".format(ou))
#             ou.validate()
#
#     validate_org_units()
from __future__ import annotations
