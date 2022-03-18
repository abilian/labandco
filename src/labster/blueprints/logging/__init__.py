"""Blueprint (and internat service) for logs."""
from __future__ import annotations

from flask_smorest import Blueprint

from labster.security import login_required

blueprint = Blueprint("logs", __name__, template_folder="templates", url_prefix="/logs")
route = blueprint.route

__all__ = ("route",)


@blueprint.before_request
@login_required
def before_request() -> None:
    # Do nothing, just require login
    pass


@route("/")
def index():
    return ""
    # entries = LogEntry.query.all()
    #
    # return render_template("logs/index.j2", entries=entries)
