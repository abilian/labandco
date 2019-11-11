import nox


@nox.session
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("pytest")


@nox.session
def lint(session):
    session.run("poetry", "install", external=True)
    session.run("flake8")
    session.run("mypy", "labster")
