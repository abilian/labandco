from __future__ import annotations

from marshmallow import fields
from marshmallow_annotations import registry

from labster.domain2.model.profile import ProfileId
from labster.domain2.model.structure import StructureId

registry.register_field_for_type(StructureId, fields.Integer)
registry.register_field_for_type(ProfileId, fields.Integer)
