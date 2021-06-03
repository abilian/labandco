# from __future__ import annotations
#
# from sqlalchemy import Column, Date, Integer, String, Unicode
#
# from labster.extensions import db
#
#
# # class StatsLine(db.Model):
# #     __tablename__ = "stats_line"
# #
# #     demande_id = Column(Integer, primary_key=True)
# #
# #     # Filtrage
# #     type_demande = Column(String, index=True, nullable=False)
# #
# #     date_soumission = Column(Date, index=True)
# #     date_finalisation = Column(Date, index=True)
# #
# #     structure_id = Column(Integer, index=True)
# #     porteur_id = Column(Integer, index=True)
# #
# #     # Champs spécifiques
# #     financeur = Column(Unicode, index=True)
# #     type_recrutement = Column(Unicode, index=True)
# #
# #     wf_state = Column(Unicode, index=True)
# #
# #     # Drilldown
# #     pole_id = Column(Integer, index=True)
# #     ufr_id = Column(Integer, index=True)
# #     labo_id = Column(Integer, index=True)
# #     departement_id = Column(Integer, index=True)
# #     equipe_id = Column(Integer, index=True)
# #
# #     # Agregations / Demande Conventions
# #     montant = Column(Integer)
# #     recrutements_prev = Column(Integer)
# #
# #     # Agregations / Demandes RH
# #     salaire_brut_mensuel = Column(Integer)
# #     cout_total_mensuel = Column(Integer)
# #
# #     # Commun Conventions / RH
# #     duree = Column(Integer)
# #
# #     # Autres
# #     duree_traitement = Column(Integer)
from __future__ import annotations
