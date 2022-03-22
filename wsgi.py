"""Create an application instance."""
from pathlib import Path


from labster.app import create_app

app = create_app()


newrelic_config = Path(__file__).parent / "newrelic.ini"
if newrelic_config.exists():
    import newrelic.agent

    newrelic.agent.initialize(newrelic_config, environment="production")

    app = newrelic.agent.WSGIApplicationWrapper(app)
