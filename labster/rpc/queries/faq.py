from __future__ import annotations

from typing import Any, Dict, List

import ramda as r
from marshmallow import Schema, fields

from labster.domain.models.faq import FaqEntry
from labster.rpc.registry import context_for


@context_for("faq")
def get_faq() -> Dict[str, List[Any]]:
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
