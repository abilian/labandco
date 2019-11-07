from __future__ import annotations

import unicodedata
from typing import Iterable, List

from flask import g

from labster.domain.models.profiles import Profile


def get_current_user() -> Profile:
    return g.current_user


def sort_by_name(iterable: Iterable) -> List:
    result = list(iterable)
    if not result:
        return []
    if hasattr(result[0], "prenom"):
        return sorted(result, key=lambda x: (x.nom, x.prenom))
    else:
        return sorted(result, key=lambda x: x.name)


def strip_accents(text: str) -> str:
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
