import nox


nox.options.reuse_existing_virtualenvs = True


@nox.session
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("pytest")


@nox.session
def lint(session):
    session.run("poetry", "install", external=True)
    session.run("flake8", "src")
    session.run("ruff", "src")
    # session.run("mypy", "src")
