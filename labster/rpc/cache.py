from __future__ import annotations

from diskcache import Cache

cache = Cache("var/cache", tag_index=True, statistics=True)
