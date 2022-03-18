from __future__ import annotations

from copy import deepcopy
from typing import Any

from flask import json
from flask_sqlalchemy import SQLAlchemy

from labster.di import injector
from labster.domain2.model.structure import StructureRepository
from labster.domain2.model.type_structure import DE, EQ
from labster.domain2.services.constants import get_constants
from labster.domain2.services.roles import Role, RoleService
from labster.types import JSONDict

from .fields import Field, FieldSet

structure_repo = injector.get(StructureRepository)
role_service = injector.get(RoleService)
db = injector.get(SQLAlchemy)


class Form:
    fieldsets: list[FieldSet] = []
    conditions: str = ""
    mode: str = "edit"
    name: str = ""
    label: str = ""

    def __init__(
        self, model=None, mode="edit", laboratoire=None, porteur=None, gestionnaire=None
    ):
        self.fieldsets = deepcopy(self.__class__.fieldsets)
        self.mode = mode

        self.post_init()

        if porteur:
            self.set_porteur(porteur)

        elif gestionnaire:
            self.set_porteurs_possibles(gestionnaire)

        elif laboratoire:
            self.set_membres_du_labo(laboratoire)

        if model is None:
            self.model = self.empty_model()
        elif isinstance(model, dict):
            self.model = model
        else:
            raise RuntimeError("Unimplemented")

    def post_init(self):
        pass

    def update_choices(self):
        """Override in subclasses."""

        self.set_structures_concernees_choices()
        self.set_contributeurs_choices()

    def set_porteurs_possibles(self, gestionnaire):
        return

        # TODO
        # roles = gestionnaire.get_roles(RoleType.GDL)
        # membres = set()
        # for role in roles:
        #     org = role.context
        #     porteurs_org = [x for x in org.get_membres() if x.has_role("porteur")]
        #     membres.update(porteurs_org)
        #
        # porteurs_du_labo = sorted(membres, key=lambda x: x.nom)
        # field = self.get_field("porteur")
        # if field:
        #     field.choices = [(m.uid, f"{m.nom} {m.prenom}") for m in porteurs_du_labo]

    def set_membres_du_labo(self, labo):
        membres_du_labo = sorted(labo.membres, key=lambda x: x.nom)
        field = self.get_field("porteur")
        if field:
            field.choices = [(m.uid, f"{m.nom} {m.prenom}") for m in membres_du_labo]

    def set_porteur(self, porteur):
        field = self.get_field("porteur")
        if field:
            field.choices = [(porteur.uid, f"{porteur.nom} {porteur.prenom}")]
            field.editable = False

    def to_dict(self) -> JSONDict:
        return {
            "name": self.name,
            "label": self.label,
            "fieldsets": [fs.to_dict() for fs in self.fieldsets],
            "fields": {f.name: f.to_dict() for f in self.fields},
            "csrf_token": "",
            "mode": self.mode,
            "constants": get_constants(),
            "conditions": self.conditions,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(), sort_keys=True, indent=4, separators=(",", ": ")
        )

    @property
    def fields(self) -> list[Field]:
        fields = []
        for fs in self.fieldsets:
            for f in fs.fields:
                if isinstance(f, Field):
                    fields.append(f)
        return fields

    def get_field(self, name: str) -> Any:
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def empty_model(self) -> JSONDict:
        model: JSONDict = {}
        for field in self.fields:
            model[field.name] = ""
        return model

    def fix_model(self, model: JSONDict) -> JSONDict:
        model = deepcopy(model)
        for field in self.fields:
            if field.name not in model:
                model[field.name] = ""
        return model

    #
    #
    #
    def set_structures_concernees_choices(self):
        field = self.get_field("structures_concernees")
        if not field:
            return

        structures = structure_repo.get_all()
        choices = [
            {"value": s.id, "label": f"{s.type}: {s.nom} ({s.sigle})"}
            for s in structures
            if s.type not in {DE, EQ}
        ]
        choices.sort(key=lambda t: t["label"])
        field.choices = choices

    def set_contributeurs_choices(self):
        field = self.get_field("contributeurs")
        if not field:
            return

        profiles = role_service.get_users_with_role(Role.PORTEUR, "*")
        profiles = [p for p in profiles if p.active]
        profiles.sort(key=lambda p: (p.nom, p.prenom))

        choices = [{"value": p.id, "label": f"{p.nom}, {p.prenom}"} for p in profiles]
        choices.sort(key=lambda t: t["label"])
        field.choices = choices
