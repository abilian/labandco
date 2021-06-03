# from __future__ import annotations
#
# from abilian.web.forms import Form, optional
# from flask import g
# from wtforms import DateField, SelectField, SelectMultipleField
#
# from labster.blueprints.bi.model import StatsLine
# from labster.blueprints.bi.util import mes_structures
# from labster.domain.models.profiles import Profile
# from labster.domain.models.unites import OrgUnit
# from labster.extensions import db
#
#
# class FilterForm(Form):
#     periode_debut = DateField(
#         "Période du", validators=(optional(),), render_kw={"placeholder": "AAAA-MM-JJ"}
#     )
#     periode_fin = DateField(
#         "Au", validators=(optional(),), render_kw={"placeholder": "AAAA-MM-JJ"}
#     )
#
#     types_demande = SelectMultipleField(
#         "Types de demande", render_kw={"class": "select2", "style": "width: 100%;"}
#     )
#     financeurs = SelectMultipleField(
#         "Financeurs", render_kw={"class": "select2", "style": "width: 100%;"}
#     )
#     types_recrutement = SelectMultipleField(
#         "Types de recrutement", render_kw={"class": "select2", "style": "width: 100%;"}
#     )
#
#     structure = SelectField(
#         "Structure",
#         validators=(optional(),),
#         render_kw={"class": "select2", "style": "width: 100%;"},
#     )
#
#     porteur = SelectField(
#         "Porteur",
#         validators=(optional(),),
#         render_kw={"class": "select2", "style": "width: 100%;"},
#     )
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.set_type_demande_choices()
#         self.set_financeur_choices()
#         self.set_types_recrutement_choices()
#         self.set_structure_choices()
#         self.set_porteur_choices()
#
#     def set_type_demande_choices(self):
#         types_demandes = db.session.query(StatsLine.type_demande).distinct().all()
#         types_demandes.sort()
#         self.types_demande.choices = [(x[0], x[0]) for x in types_demandes]
#
#     def set_financeur_choices(self):
#         financeurs = (
#             db.session.query(StatsLine.financeur)
#             .filter(StatsLine.type_demande == "Convention de recherche")
#             .filter(StatsLine.financeur != None)
#             .filter(StatsLine.financeur != "")
#             .order_by(StatsLine.financeur)
#             .distinct()
#             .all()
#         )
#         self.financeurs.choices = [(x[0], x[0]) for x in financeurs]
#
#     def set_types_recrutement_choices(self):
#         types_recrutement = (
#             db.session.query(StatsLine.type_recrutement)
#             .filter(StatsLine.type_demande == "Recrutement")
#             .filter(StatsLine.type_recrutement != None)
#             .distinct()
#             .all()
#         )
#         self.types_recrutement.choices = [(x[0], x[0]) for x in types_recrutement]
#
#     def set_porteur_choices(self):
#         porteur_ids = (
#             db.session.query(StatsLine.porteur_id)
#             .filter(StatsLine.porteur_id != None)
#             .distinct()
#             .all()
#         )
#         porteurs = [Profile.query.get(id) for id in porteur_ids]
#         porteurs.sort(key=lambda x: (x.nom, x.prenom))
#         self.porteur.choices = [("", "-")] + [
#             (str(p.id), p.full_name) for p in porteurs
#         ]
#
#     def set_structure_choices(self):
#         equipe_ids = (
#             db.session.query(StatsLine.equipe_id)
#             .filter(StatsLine.equipe_id != None)
#             .distinct()
#             .all()
#         )
#         departement_ids = (
#             db.session.query(StatsLine.departement_id)
#             .filter(StatsLine.departement_id != None)
#             .distinct()
#             .all()
#         )
#         labo_ids = (
#             db.session.query(StatsLine.labo_id)
#             .filter(StatsLine.labo_id != None)
#             .distinct()
#             .all()
#         )
#         ufr_ids = (
#             db.session.query(StatsLine.ufr_id)
#             .filter(StatsLine.ufr_id != None)
#             .distinct()
#             .all()
#         )
#         pole_ids = (
#             db.session.query(StatsLine.pole_id)
#             .filter(StatsLine.pole_id != None)
#             .distinct()
#             .all()
#         )
#
#         user = g.current_user
#         if user.has_role("directeur"):
#             structures = mes_structures(user)
#
#         else:
#             ids = labo_ids + departement_ids + equipe_ids + ufr_ids + pole_ids
#             structure_ids = [x[0] for x in ids]
#             structures = [OrgUnit.query.get(id) for id in structure_ids]
#
#         def path(structure):
#             keys = ["pole", "ufr", "laboratoire", "departement", "equipe"]
#             path = []
#             for key in keys:
#                 value = getattr(structure, key)
#                 if value:
#                     path.append(value.nom)
#                 else:
#                     path.append("")
#             return path
#
#         to_sort = [(path(structure), structure) for structure in structures]
#         to_sort.sort()
#         structures = [t[1] for t in to_sort]
#
#         def make_label(structure):
#             prefix = "-" * structure.depth
#             return f"{prefix}{structure.nom} ({structure.type})"
#
#         self.structure.choices = [("", "-")] + [
#             (str(s.id), make_label(s)) for s in structures
#         ]
from __future__ import annotations
