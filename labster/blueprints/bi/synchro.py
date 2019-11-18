# from __future__ import annotations
#
# from functools import singledispatch
#
# from labster.domain.models.demandes import Demande, DemandeAvenantConvention, \
#     DemandeConvention, DemandeRH
# from labster.domain.services.calculs_couts import get_ctx_for_demande
# from labster.extensions import db
#
# from .model import StatsLine
#
#
# def sync_all():
#     StatsLine.query.delete()
#
#     demandes = Demande.query.all()
#     for demande in demandes:
#         line = sync(demande)
#         if line:
#             db.session.add(line)
#
#     db.session.commit()
#
#
# def sync(demande):
#     if demande.wf_state == "EN_EDITION":
#         keep = False
#         for state in demande.wf_history:
#             transition = state.get("transition")
#             if transition in (
#                 "REQUERIR_MODIFICATION_DIR",
#                 "REQUERIR_MODIFICATION_DGRTT",
#             ):
#                 keep = True
#         if not keep:
#             return
#
#     data = {
#         "demande_id": demande.id,
#         "type_demande": demande.type,
#         "wf_state": demande.wf_state,
#         "date_soumission": demande.date_soumission,
#         "date_finalisation": demande.date_finalisation,
#     }
#
#     if demande.porteur:
#         data["porteur_id"] = demande.porteur_id
#     else:
#         data["porteur_id"] = None
#
#     structure = demande.structure
#     if structure:
#         data["structure_id"] = structure.id
#         data["equipe_id"] = get_id(structure.equipe)
#         data["departement_id"] = get_id(structure.departement)
#         data["labo_id"] = get_id(structure.laboratoire)
#         data["ufr_id"] = get_id(structure.ufr)
#         data["pole_id"] = get_id(structure.pole)
#
#     update_data = sync_specific(demande)
#     # if update_data is None:
#     #     return None
#
#     data.update(update_data)
#     line = StatsLine(**data)
#     return line
#
#
# @singledispatch
# def sync_specific(demande):
#     data = {}
#     return data
#
#
# @sync_specific.register(DemandeConvention)
# def _(demande):
#     data = {
#         "montant": pick_integer(demande, "montant_financement"),
#         "recrutements_prev": pick_integer(demande, "nombre_recrutements"),
#         "duree": pick_integer(demande, "duree_previsionnelle"),
#         "financeur": getattr(demande, "type_financeur", ""),
#     }
#     return data
#
#
# @sync_specific.register(DemandeAvenantConvention)
# def _1(demande):
#     data = {"financeur": getattr(demande, "type_financeur", "")}
#     return data
#
#
# @sync_specific.register(DemandeRH)
# def _2(demande):
#     # print(demande.id)
#     data = {
#         "duree": demande.duree_mois or 0,
#         "type_recrutement": (
#             getattr(demande, "nature_du_recrutement", "")
#             + " | "
#             + getattr(demande, "type_de_demande", "")
#         ),
#     }
#
#     ctx = get_ctx_for_demande(demande)
#     data["salaire_brut_mensuel"] = ctx["salaire_brut"]
#     data["cout_total_mensuel"] = ctx["cout_total"]
#
#     return data
#
#
# # # TODO
# # @sync_specific.register(DemandePiLogiciel)
# # def _3(demande):
# #     data = {}
# #     return data
# #
# #
# # # TODO
# # @sync_specific.register(DemandePiInvention)
# # def _4(demande):
# #     data = {}
# #     return data
# #
# #
# # # TODO
# # @sync_specific.register(DemandeAutre)
# # def _5(demande):
# #     data = {}
# #     return data
#
#
# def pick_integer(demande, field_name):
#     try:
#         value = int(getattr(demande, field_name).replace(" ", ""))
#         if value > 2147483647:
#             value = 2147483647
#     except (ValueError, AttributeError):
#         # print(getattr(demande, field_name, None))
#         # traceback.print_exc()
#         value = 0
#     return value
#
#
# def get_id(obj):
#     if obj:
#         return obj.id
#     else:
#         return None
from __future__ import annotations
