from __future__ import annotations

from pathlib import Path
from typing import Callable

from werkzeug.utils import import_string

registry: dict[str, Callable] = {}


def context_for(name: str) -> Callable:
    def wrap(f):
        f._exposed = True
        registry[name] = f
        return f

    return wrap


def register_submodules():
    here = "labster.rpc"
    subdirs = ["commands", "queries", "bi"]

    import_string(f"{here}.context")

    this_dir = Path(__file__).parent
    for subdir in subdirs:
        for path in (this_dir / subdir).glob("*.py"):
            name = path.parts[-1][0:-3]
            if name == "__init__":
                continue

            fqn = f"{here}.{subdir}.{name}"
            import_string(fqn)
