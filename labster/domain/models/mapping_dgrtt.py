from __future__ import annotations

from abilian.core.models import IdMixin
from flask_sqlalchemy import BaseQuery
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from labster.extensions import db

from .profiles import Profile
from .unites import OrgUnit


class MappingDgrttQuery(BaseQuery):
    def get_for_ou(self, ou):
        return self.filter(MappingDgrtt.ou_recherche_id == ou.id).all()


class MappingDgrtt(IdMixin, db.Model):
    __tablename__ = "mapping_dgrtt"
    query_class = MappingDgrttQuery

    ou_recherche_id = Column(Integer, ForeignKey(OrgUnit.id), nullable=False)
    ou_recherche: OrgUnit = relationship(
        OrgUnit,
        foreign_keys=[ou_recherche_id],
        backref=backref("mapping_dgrtt1", cascade="all,delete"),
    )

    bureau_dgrtt = Column(String, nullable=False)

    contact_dgrtt_id = Column(Integer, ForeignKey(Profile.id), nullable=False)
    contact_dgrtt = relationship(
        Profile,
        foreign_keys=[contact_dgrtt_id],
        backref=backref("mapping_dgrtt3", cascade="all,delete"),
    )

    def __repr__(self) -> str:
        return "<MappingDgrtt ou={} bureau={} contact={}>".format(
            self.ou_recherche.sigle_ou_nom, self.bureau_dgrtt, self.contact_dgrtt.uid
        )
