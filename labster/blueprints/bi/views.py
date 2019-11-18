# from __future__ import annotations
#
# import dateutil.parser
# import pandas as pd
# from flask import g, render_template, request
# from werkzeug.exceptions import Forbidden
#
# from labster.blueprints.bi.forms import FilterForm
# from labster.blueprints.bi.util import mes_structures
# from labster.domain.models.demandes import AVENANT_CONVENTION, CONVENTION, \
#     PI_INVENTION, PI_LOGICIEL, RECRUTEMENT
# from labster.domain.models.profiles import Profile
# from labster.domain.models.unites import OrgUnit
# from labster.domain.models.workflow import ALL_STATES
#
# from . import route
# from .model import StatsLine
#
# SECONDS_IN_DAY = 60.0 * 60 * 24
# ALLOWED_ROLES = ["alc", "directeur", "chef de bureau", "gouvernance", "direction dgrtt"]
#
# #
# @route("/")
# def home():
#     user = g.current_user  # type: Profile
#
#     if user.is_anonymous or not user.has_role(ALLOWED_ROLES):
#         raise Forbidden()
#
#     form = FilterForm(request.args)
#     form.validate()
#     ctx = {"title": "Statistiques", "form": form}
#
#     # Filtrage
#     periode_debut = form.periode_debut.data
#     periode_fin = form.periode_fin.data
#     types_demande = form.types_demande.data
#     types_recrutement = form.types_recrutement.data
#     financeurs = form.financeurs.data
#     structure_id = form.structure.data
#     porteur_id = form.porteur.data
#
#     query = StatsLine.query
#     if periode_debut:
#         query = query.filter(StatsLine.date_soumission >= periode_debut)
#     if periode_fin:
#         query = query.filter(StatsLine.date_soumission <= periode_fin)
#     if types_demande:
#         query = query.filter(StatsLine.type_demande.in_(types_demande))
#     if types_recrutement:
#         query = query.filter(StatsLine.type_recrutement.in_(types_recrutement))
#     if financeurs:
#         query = query.filter(StatsLine.financeur.in_(financeurs))
#     if porteur_id not in ("", "None", None):
#         query = query.filter(StatsLine.porteur_id == porteur_id)
#
#     if structure_id not in ("", "None", None):
#         structure_id = int(structure_id)
#         if user.has_role("recherche"):
#             structures = mes_structures(user)
#             if structure_id not in {s.id for s in structures}:
#                 raise Forbidden()
#
#         structure = OrgUnit.query.get(structure_id)
#         descendant_ids = [s.id for s in structure.descendants()]
#         query = query.filter(
#             StatsLine.structure_id.in_([structure_id] + descendant_ids)
#         )
#
#     elif user.has_role("directeur"):
#         structures = mes_structures(user)
#         query = query.filter(StatsLine.structure_id.in_([s.id for s in structures]))
#
#     # Stats
#     for state in ALL_STATES:
#         state_id = state.id.lower()
#         ctx["nb_" + state_id] = query.filter(StatsLine.wf_state == state.id).count()
#
#     ctx["nb_en_cours"] = sum(
#         ctx[id]
#         for id in [
#             "nb_en_edition",
#             "nb_en_validation",
#             "nb_en_verification",
#             "nb_en_instruction",
#         ]
#     )
#     ctx["nb_archivee"] = sum(
#         ctx[id] for id in ["nb_traitee", "nb_rejetee", "nb_abandonnee"]
#     )
#     ctx["nb_total"] = ctx["nb_en_cours"] + ctx["nb_archivee"]
#     assert ctx["nb_total"] == query.count()
#
#     stats = {
#         "conventions": make_conventions_stats(query),
#         "rh": make_rh_stats(query),
#         "avenants": make_avenants_stats(query),
#         "pi_logiciel": make_pi_logiciel_stats(query),
#         "pi_invention": make_pi_invention_stats(query),
#         "duree_traitement": make_duree_traitement_stats(query),
#     }
#
#     ctx["stats"] = stats
#
#     return render_template("bi/home.html", **ctx)
#
#
# def parse_date(s):
#     return dateutil.parser.parse(s)
#
#
# def make_rh_stats(query):
#     lines = query.filter(StatsLine.type_demande == RECRUTEMENT).all()
#     result = make_stats(lines, ["duree", "salaire_brut_mensuel", "cout_total_mensuel"])
#     result["count"] = len(lines)
#     return result
#
#
# def make_conventions_stats(query):
#     lines = query.filter(StatsLine.type_demande == CONVENTION).all()
#     result = make_stats(lines, ["montant", "recrutements_prev", "duree"])
#     result["count"] = len(lines)
#     return result
#
#
# def make_avenants_stats(query):
#     lines = query.filter(StatsLine.type_demande == AVENANT_CONVENTION).all()
#     result = make_stats(lines, [])
#     result["count"] = len(lines)
#     return result
#
#
# def make_pi_logiciel_stats(query):
#     lines = query.filter(StatsLine.type_demande == PI_LOGICIEL).all()
#     result = make_stats(lines, [])
#     result["count"] = len(lines)
#     return result
#
#
# def make_pi_invention_stats(query):
#     lines = query.filter(StatsLine.type_demande == PI_INVENTION).all()
#     result = make_stats(lines, [])
#     result["count"] = len(lines)
#     return result
#
#
# def make_duree_traitement_stats(query):
#     def duree_traitement(line):
#         if line.date_soumission and line.date_finalisation:
#             dt = line.date_finalisation - line.date_soumission
#             days = dt.days + dt.seconds / SECONDS_IN_DAY
#             return days
#         else:
#             return None
#
#     lines = query.all()
#     series = pd.Series([duree_traitement(line) for line in lines])
#     return [
#         series.mean(),
#         series.median(),
#         series.std(),
#         series.min(),
#         series.max(),
#         series.sum(),
#     ]
#
#
# def make_stats(lines, attrs):
#     result = {}
#     for attr in attrs:
#         series = pd.Series([getattr(line, attr) for line in lines])
#         result[attr] = [
#             series.mean(),
#             series.median(),
#             series.std(),
#             series.min(),
#             series.max(),
#             series.sum(),
#         ]
#     return result
from __future__ import annotations
