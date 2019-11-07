from __future__ import annotations

import time
from functools import singledispatch, wraps

import flask
from flask_sqlalchemy import connection_stack

from labster.domain2.model.profile import Profile
from labster.domain2.model.structure import Structure
from labster.domain.models.demandes import Demande
from labster.domain.models.profiles import Profile as OldProfile
from labster.domain.models.unites import OrgUnit


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


#
# Old stuff. Remove when ready.
#
@url_for.register(OldProfile)
def url_for_old_profile(profile: OldProfile, **kw) -> str:
    return flask.url_for("main.home", _anchor=f"/annuaire/users/{profile.id}", **kw)


@url_for.register(OrgUnit)
def url_for_org_unit(org_unit: OrgUnit, **kw) -> str:
    return flask.url_for(
        "main.home", _anchor=f"/annuaire/structures/{org_unit.id}", **kw
    )


#
# Other stuff
#
def timeit(method):
    @wraps(method)
    def timed(*args, **kw):
        ctx = connection_stack.top
        ctx.sqlalchemy_queries = []

        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int((te - ts) * 1000)
        else:
            print(f"{method.__name__!r} {(te - ts) * 1000:2.2f} ms")
            if args:
                print(f"args: {args}")
            if kw:
                print(f"kwargs: {kw}")

        queries = ctx.sqlalchemy_queries
        sql_time = sum(query.duration for query in queries)
        print(f"SQL queries (# = {len(queries)}, time={sql_time*1000}ms):")
        # for i, query in enumerate(queries):
        #     print(i, query.statement)
        #     print(i, query.parameters)
        #     print(i, query.duration)
        #     print(i, query.context)
        # print(f"SQL queries (# = {len(queries)}, time={sql_time*1000}ms):")

        print()
        return result

    return timed
