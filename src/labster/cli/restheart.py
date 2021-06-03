"""Restheart related commands."""
from __future__ import annotations

from flask.cli import AppGroup, with_appcontext

import labster.bus

restheart = AppGroup("restheart")


@restheart.command("init")
@with_appcontext
def restheart_init():
    """Create needed collections in RestHeart DB."""
    labster.bus.init()


@restheart.command("sync")
@with_appcontext
def restheart_sync_all():
    """Sync (push all data) to RestHeart DB."""
    labster.bus.sync_all_objects()
