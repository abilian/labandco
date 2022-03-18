from __future__ import annotations

from typing import Any

import ramda as r
from marshmallow import Schema, fields
from werkzeug.exceptions import Forbidden

from labster.domain2.services.constants import get_constant
from labster.domain2.services.roles import Role
from labster.domain.models.faq import FaqEntry
from labster.rpc.registry import context_for
from labster.security import get_current_profile


@context_for("faq")
def get_faq() -> dict[str, list[Any]]:
    entries = FaqEntry.query.order_by(FaqEntry.view_count.desc()).all()
    groups = sorted(r.group_by(lambda e: e.category, entries).items())

    result = []
    for k, v in groups:
        v = sorted(v, key=lambda x: -(x.view_count or 0))
        data = FaqEntrySchema().dump(v, many=True).data
        result.append([k, data])

    return {"categories": result, "entries": []}


class FaqEntrySchema(Schema):
    id = fields.String()
    title = fields.String()
    body = fields.String()
    category = fields.String()

    view_count = fields.Method("get_view_count")

    def get_view_count(self, obj: FaqEntry):
        return obj.view_count or 0


#
# Admin
#
@context_for("faq_admin")
def faq_admin():
    check_user_can_edit()
    entries = FaqEntry.query.order_by(FaqEntry.id).all()
    data = FaqEntrySchema().dump(entries, many=True).data

    categories = get_constant("faq_categories", [])
    return {"entries": data, "categories": categories}


def check_user_can_edit():
    profile = get_current_profile()
    if profile.has_role(Role.ADMIN_CENTRAL) or profile.has_role(Role.FAQ_EDITOR):
        return

    raise Forbidden
