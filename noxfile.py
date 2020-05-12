import nox

PYTHON_VERSIONS = ["3.7", "3.8", "3.9"]

nox.options.reuse_existing_virtualenvs = True


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("pytest")


@nox.session
def lint(session):
    session.run("poetry", "install", external=True)
    session.run("flake8", "labster")
    session.run("mypy", "labster")
