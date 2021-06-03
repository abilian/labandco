from __future__ import annotations

import functools

from diskcache.core import ENOVAL, args_to_key, full_name
from flask import g


def memoize():
    def decorator(func):
        """Decorator created by memoize() for callable `func`."""
        base = (full_name(func),)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper for callable to cache arguments and return values."""
            key = wrapper.__cache_key__(*args, **kwargs)
            result = g.cache.get(key, ENOVAL)

            if result is ENOVAL:
                result = func(*args, **kwargs)
                g.cache[key] = result

            return result

        def __cache_key__(*args, **kwargs):
            """Make key for cache given function arguments."""
            return args_to_key(base, args, kwargs, False)

        wrapper.__cache_key__ = __cache_key__
        return wrapper

    return decorator
