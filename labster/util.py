from __future__ import annotations

import unicodedata
from functools import singledispatch
from typing import Iterable, List

import flask

from labster.domain2.model.demande import Demande
from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure


@singledispatch
def url_for(obj, **kw) -> str:
    raise RuntimeError(f"Unknown type ({type(obj)}) for obj {obj}")


@url_for.register(str)
def url_for_str(obj: str, **kw) -> str:
    return flask.url_for(obj, **kw)


@url_for.register(Profile)
def url_for_profile(profile: Profile, **kw) -> str:
    return flask.url_for("main.home", _anchor=f"/annuaire/users/{profile.id}", **kw)


@url_for.register(Structure)
def url_for_structure(structure: Structure, **kw) -> str:
    return flask.url_for(
        "main.home", _anchor=f"/annuaire/structures/{structure.id}", **kw
    )


@url_for.register(Demande)
def url_for_demande(demande: Demande, **kw) -> str:
    return flask.url_for("main.home", _anchor=f"/demandes/{demande.id}", **kw)


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
