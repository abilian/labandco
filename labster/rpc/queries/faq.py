from __future__ import annotations

from typing import Any, Dict, List

from marshmallow import Schema, fields

from labster.domain.models.faq import FaqEntry
from labster.rpc.cache import cache
from labster.rpc.registry import context_for


@context_for("faq")
@cache.memoize(tag="faq")
def get_faq() -> Dict[str, List[Any]]:
    entries = FaqEntry.query.all()
    data = FaqEntrySchema().dump(entries, many=True).data
    return {"entries": data}


class FaqEntrySchema(Schema):
    id = fields.String()
    title = fields.String()
    body = fields.String()
    category = fields.String()
