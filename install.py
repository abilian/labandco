#!/usr/bin/env python
import os
import sys
from pathlib import Path

APP_NAME = "Lab&Co"
PYTHON_VERSION = "3.7.5"


def run(cmd):
    print(f"> {cmd}")
    status = os.system(cmd)
    print(f"status = {status}")
    return status


print(f"Going to install {APP_NAME}")
print("Press Y to confirm")
answ = input()
if answ.lower() != "y":
    sys.exit()

pyenv_root = Path(os.environ["HOME"]) / ".pyenv"

if not pyenv_root.exists():
    print("Installing pyenv")
    if not run("curl https://pyenv.run | bash"):
        print("! Ensure that you have 'curl' installed")
        sys.exit()

else:
    print("Pyenv seems to be alredy installed.")

print()

if not (pyenv_root / "versions" / PYTHON_VERSION).exists():
    print(f"Installing Python {PYTHON_VERSION}")
    if not run(f"pyenv install {PYTHON_VERSION}"):
        print(f"! Couldn't install Python version {PYTHON_VERSION}")
        sys.exit()

else:
    print(f"Python {PYTHON_VERSION} seems to be alredy installed. Skipping.")

print()

if not Path("env").exists():
    print("Creating virtual env")
    cmd = f"{pyenv_root}/versions/{PYTHON_VERSION}/bin/python3.7 -m venv env"
    if run(cmd):
        print("! Couldn't created virtualenv at 'env'")
        sys.exit()

else:
    print("Reusing existing virtual env 'env'.")


print("Installing or updating back-end (Python) dependencies")
cmd = "./env/bin/pip install -r requirements.txt ."
if run(cmd):
    print("! Couldn't install back-end dependencies")
    sys.exit()


print("Installing or updating front-end (JavaScript) dependencies")
cmd = "yarn --cwd front"
if run(cmd):
    print("! Couldn't install front-end dependencies")
    sys.exit()


print()
print("Everything should be fine now.")
print()

print("Available commands are:")
print(os.popen("./env/bin/flask").read())
print()

print("Now run '. env/bin/activate' from your shell and you can start developping.")
