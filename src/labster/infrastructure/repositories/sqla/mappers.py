from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from injector import inject

# types_demande = [cls._type.value for cls in _REGISTRY.values()]


class Mapper:
    @inject
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.metadata = db.metadata

        # self.map_profiles()
        # self.map_structures()
        # self.map_demandes()

    # def map_profiles(self):
    #     profiles = Table(
    #         "v3_profiles",
    #         self.db.metadata,
    #         #
    #         Column("id", String(36), primary_key=True),
    #         Column("uid", String(64), unique=True, nullable=True),
    #         Column("old_id", Integer, unique=True, nullable=True),
    #         Column("old_uid", String(64), unique=True, nullable=True),
    #         Column("login", String(64), default="", nullable=False),
    #         #
    #         Column("nom", String, default="", nullable=False),
    #         Column("prenom", String, default="", nullable=False),
    #         Column("email", String, default="", nullable=False),
    #         Column("adresse", String, default="", nullable=False),
    #         Column("telephone", String, default="", nullable=False),
    #         #
    #         Column("active", Boolean, default=False, nullable=False),
    #         Column("affectation", String, default="", nullable=False),
    #         Column("fonctions", JSON, nullable=False),
    #         #
    #         Column("preferences_notifications", Integer, default=0, nullable=False),
    #     )
    #
    #     mapper(Profile, profiles)
    #
    # def map_structures(self):
    #     hierarchy = Table(
    #         "v3_hierarchy",
    #         self.db.metadata,
    #         Column("parent_id", String(36), ForeignKey("v3_structures.id")),
    #         Column("child_id", String(36), ForeignKey("v3_structures.id")),
    #     )
    #
    #     structures = Table(
    #         "v3_structures",
    #         self.db.metadata,
    #         #
    #         Column("id", String(36), primary_key=True),
    #         Column("old_id", Integer),
    #         Column("active", Boolean),
    #         Column("type_name", String),
    #         #
    #         Column("nom", String),
    #         Column("sigle", String),
    #         Column("dn", String),
    #         Column("old_dn", String),
    #         Column("email", String),
    #         #
    #         Column("permettre_reponse_directe", Boolean),
    #         Column("permettre_soummission_directe", Boolean),
    #         #
    #     )
    #     mapper(
    #         Structure,
    #         structures,
    #         properties={
    #             "children": relationship(
    #                 Structure,
    #                 secondary=hierarchy,
    #                 primaryjoin=(hierarchy.c.parent_id == structures.c.id),
    #                 secondaryjoin=(hierarchy.c.child_id == structures.c.id),
    #                 collection_class=set,
    #                 backref=backref("parents", collection_class=set),
    #             )
    #         },
    #     )
    #
    # def map_demandes(self):
    #     demandes = Table(
    #         "v3_demandes",
    #         self.db.metadata,
    #         #
    #         Column("id", Integer, primary_key=True),
    #         Column("old_id", Integer),
    #         Column(
    #             "type",
    #             Enum(*types_demande, name="type_demande"),
    #             nullable=False,
    #             index=True,
    #         ),
    #         Column("created_at", DateTime),
    #         Column("updated_at", DateTime),
    #         #
    #         Column("nom", String),
    #         Column("name", String),
    #         Column("active", Boolean),
    #         Column("editable", Boolean),
    #         Column("no_infolab", String),
    #         Column("no_eotp", String),
    #         # Relations
    #         Column("contact_labco_id", String(36), ForeignKey("v3_profiles.id")),
    #         Column("gestionnaire_id", String(36), ForeignKey("v3_profiles.id")),
    #         Column("porteur_id", String(36), ForeignKey("v3_profiles.id")),
    #         Column("structure_id", String(36), ForeignKey("v3_structures.id")),
    #         #
    #         Column("data", JSON),
    #         Column("past_versions", JSON),
    #         Column("form_state", JSON),
    #         Column("attachments", JSON),
    #         Column("feuille_cout", JSON),
    #         Column("data", JSON),
    #         Column("documents_generes", JSON),
    #         # Workflow
    #         # wf_state = Column(WF_ENUM, default=EN_EDITION.id, nullable=False, index=True)
    #         Column("wf_state", String),
    #         Column("wf_date_derniere_action", DateTime),
    #         Column("wf_retard", Integer),
    #         Column("wf_history", JSON),
    #         Column("wf_data", JSON),
    #         Column("wf_state", String),
    #         # wf_stage_id = Column(Integer, ForeignKey(OrgUnit.id), index=True, nullable=True)
    #         # wf_stage = relationship(
    #         #     OrgUnit, primaryjoin=remote(Entity.id) == foreign(wf_stage_id)
    #         # )
    #         #
    #         # #: id de la personne responsable de la tâche en cours
    #         # wf_current_owner_id = Column(
    #         #     Integer, ForeignKey(Profile.id), index=True, nullable=True
    #         # )
    #         # #: la personne responsable de la tâche en cours
    #         # wf_current_owner = relationship(
    #         #     Profile, primaryjoin=remote(Entity.id) == foreign(wf_current_owner_id)
    #         # )
    #     )
    #
    #     properties = {
    #         "contact_labco": relationship(
    #             Profile, foreign_keys=[demandes.c.contact_labco_id]
    #         ),
    #         "porteur": relationship(Profile, foreign_keys=[demandes.c.porteur_id]),
    #         "gestionnaire": relationship(
    #             Profile, foreign_keys=[demandes.c.gestionnaire_id]
    #         ),
    #         "structure": relationship(Structure),
    #     }
    #     mapper(
    #         Demande,
    #         demandes,
    #         polymorphic_on=demandes.c.type,
    #         polymorphic_identity="none",
    #         properties=properties,
    #     )
    #     for cls in _REGISTRY.values():
    #         mapper(
    #             cls, demandes, inherits=Demande, polymorphic_identity=cls._type.value,
    #         )
