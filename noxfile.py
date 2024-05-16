import nox
from nox import Session

PYTHON_VERSIONS = ["3.10", "3.11", "3.12"]

nox.options.reuse_existing_virtualenvs = True


@nox.session(python=PYTHON_VERSIONS)
def tests(session: Session):
    session.run("poetry", "install", external=True)
    session.run("pytest")


@nox.session
def lint(session: Session):
    session.run("poetry", "install", external=True)
    session.run("flake8", "src")
    session.run("ruff", "src")
    # session.run("mypy", "src")
