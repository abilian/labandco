from __future__ import annotations

from typing import Any, Dict, List

from marshmallow import Schema, fields

from labster.blueprints.util import get_current_user
from labster.domain.models.profiles import Profile

from .. import route


class UserSchema(Schema):
    nom = fields.String()
    prenom = fields.String()
    uid = fields.String()
    id = fields.String()

    roles = fields.Method("get_roles")

    def get_roles(self, obj: Profile) -> List[Any]:
        assert isinstance(obj, Profile)
        return []


@route("/auth/self")
def self() -> Dict:
    user = get_current_user()

    user_dto = UserSchema().dump(user).data
    return {"data": user_dto}
