"""Create an application instance."""
from pathlib import Path

import newrelic.agent

from labster.app import create_app

newrelic_config = Path(__file__).parent / "newrelic.ini"
assert newrelic_config.exists()

newrelic.agent.initialize(newrelic_config, environment="production")

app = create_app()
app = newrelic.agent.WSGIApplicationWrapper(app)
