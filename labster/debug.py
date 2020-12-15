"""Debug tooling."""
from __future__ import annotations

import sys
import time
from functools import wraps

from flask_sqlalchemy import connection_stack


def timeit(method):
    @wraps(method)
    def timed(*args, **kw):
        ctx = connection_stack.top
        ctx.sqlalchemy_queries = []

        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        # Print report
        print(78 * "-")
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

        print(78 * "-")
        print()
        sys.stdout.flush()
        return result

    return timed
