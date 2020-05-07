from __future__ import annotations

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Unicode

from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.extensions import db


class StatsLine(db.Model):
    __tablename__ = "v3_stats_line"

    demande_id = Column(Integer, primary_key=True)

    # Filtrage
    type_demande = Column(String, index=True, nullable=False)

    date_soumission = Column(Date, index=True)
    date_finalisation = Column(Date, index=True)

    # structure_id = Column(Integer, index=True)
    # porteur_id = Column(Integer, index=True)
    porteur_id = Column(String(36), ForeignKey(Profile.id), index=True)
    structure_id = Column(String(36), ForeignKey(Structure.id), index=True)

    # Champs spécifiques
    financeur = Column(Unicode, index=True)
    type_recrutement = Column(Unicode, index=True)

    wf_state = Column(Unicode, index=True)

    # Drilldown
    l1 = Column(String(36), ForeignKey(Structure.id), index=True)
    l2 = Column(String(36), ForeignKey(Structure.id), index=True)
    l3 = Column(String(36), ForeignKey(Structure.id), index=True)
    l4 = Column(String(36), ForeignKey(Structure.id), index=True)
    l5 = Column(String(36), ForeignKey(Structure.id), index=True)
    l6 = Column(String(36), ForeignKey(Structure.id), index=True)
    l7 = Column(String(36), ForeignKey(Structure.id), index=True)
    l8 = Column(String(36), ForeignKey(Structure.id), index=True)
    l9 = Column(String(36), ForeignKey(Structure.id), index=True)
    l10 = Column(String(36), ForeignKey(Structure.id), index=True)

    # Agregations / Demande Conventions
    montant = Column(Integer)
    recrutements_prev = Column(Integer)

    # Agregations / Demandes RH
    salaire_brut_mensuel = Column(Integer)
    cout_total_mensuel = Column(Integer)

    # Commun Conventions / RH
    duree = Column(Integer)

    # Autres
    duree_traitement = Column(Integer)
