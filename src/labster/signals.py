from __future__ import annotations

from blinker import Namespace

namespace = Namespace()

# Used for synchronization w/ restheart
model_saved = namespace.signal("model-saved")
