from __future__ import annotations

from labster.domain2.model.demande import _REGISTRY, Demande, \
    DemandeRepository, DemandeRH


def test_single():
    demande = DemandeRH()
    assert isinstance(demande, Demande)


def test_empty_constructors():
    for cls in _REGISTRY.values():
        demande = cls()
        assert isinstance(demande, cls)
        assert isinstance(demande, Demande)


def test_repo(injector, db):
    repo = injector.get(DemandeRepository)

    for cls in _REGISTRY.values():
        demande = cls()
        repo.put(demande)

    repo.clear()
