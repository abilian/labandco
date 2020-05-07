from __future__ import annotations

from flask import request
from jsonrpcserver import method


@method
def exit():
    func = request.environ.get("werkzeug.server.shutdown")
    func()
