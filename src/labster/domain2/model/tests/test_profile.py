from __future__ import annotations

from labster.domain2.model.profile import Profile


def test_1():
    profile = Profile(nom="NOM", prenom="Prenom")
    assert profile.full_name == "Prenom NOM"


def test_2():
    profile = Profile()
    assert profile.prenom == ""
    assert profile.nom == ""
