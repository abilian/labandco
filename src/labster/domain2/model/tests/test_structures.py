from __future__ import annotations

from injector import Injector

from labster.domain2.model.structure import Structure, StructureRepository
from labster.domain2.model.type_structure import CO, DU, FA, LA, UN


def test_single():
    universite = Structure(nom="Sorbonne Université", type_name=UN.name, sigle="SU")
    assert universite.nom == "Sorbonne Université"
    assert universite.name == "Sorbonne Université"
    assert universite.sigle_ou_nom == "SU"
    assert universite.is_reelle
    assert universite.active
    assert len(universite.ancestors) == 0
    assert len(universite.descendants) == 0
    universite.check()

    universite.delete()
    assert not universite.active


def test_hierarchy():
    universite = Structure(nom="Sorbonne Université", type_name=UN.name)
    fac_sciences = Structure(nom="Faculté des Sciences", type_name=FA.name)
    assert universite not in fac_sciences.parents
    assert fac_sciences not in universite.children

    universite.add_child(fac_sciences)
    assert universite in fac_sciences.parents
    assert fac_sciences in universite.children
    assert universite.depth == 0
    assert fac_sciences.depth == 1
    assert fac_sciences.ancestors == [universite]
    universite.check()
    fac_sciences.check()

    universite.remove_child(fac_sciences)
    assert universite not in fac_sciences.parents
    assert fac_sciences not in universite.children
    assert universite.depth == 0
    assert fac_sciences.depth == 0
    universite.check()
    fac_sciences.check()

    fac_sciences.add_parent(universite)
    assert universite in fac_sciences.parents
    assert fac_sciences in universite.children
    assert universite.depth == 0
    assert fac_sciences.depth == 1
    universite.check()
    fac_sciences.check()

    fac_sciences.remove_parent(universite)
    assert universite not in fac_sciences.parents
    assert fac_sciences not in universite.children
    assert universite.depth == 0
    assert fac_sciences.depth == 0
    universite.check()
    fac_sciences.check()


def test_deep_hierarchy():
    universite = Structure(nom="Sorbonne Université", type_name=UN.name)
    fac = Structure(nom="Faculté", type_name=FA.name)
    composante = Structure(nom="Composante", type_name=CO.name)
    labo = Structure(nom="Labo", type_name=LA.name)

    universite.add_child(fac)
    fac.add_child(composante)
    composante.add_child(labo)

    universite.check()
    fac.check()
    composante.check()
    labo.check()

    assert labo.ancestors == [composante, fac, universite]


def test_constraints_on_parent():
    un = Structure(nom="Sorbonne Université", type_name=UN.name)
    la = Structure(nom="Labo", type_name=LA.name)
    du = Structure(nom="DU", type_name=DU.name)

    assert not un.can_have_parent(un)
    assert not un.can_have_parent(la)
    assert not la.can_have_parent(la)
    assert not la.can_have_parent(un)

    assert not un.can_have_parent(du)
    assert du.can_have_parent(un)

    assert not un.can_have_child(un)
    assert not un.can_have_child(la)
    assert not la.can_have_child(la)
    assert not la.can_have_child(un)

    assert un.can_have_child(du)
    assert not du.can_have_child(un)


def test_repo(injector: Injector, db_session):
    repo = injector.get(StructureRepository)

    universite = Structure(
        nom="Sorbonne Université", type_name=UN.name, sigle="SU", dn="Top"
    )
    fac_sciences = Structure(nom="Faculté des Sciences", type_name=FA.name)
    repo.put(universite)
    repo.put(fac_sciences)
    assert universite in repo.get_all()
    assert fac_sciences in repo.get_all()
    repo.check_all()

    assert universite == repo.get_by_id(universite.id)
    assert universite == repo.get_by_dn(universite.dn)
    assert universite == repo.get_by_sigle(universite.sigle)

    universite.add_child(fac_sciences)
    assert universite in repo.get_all()
    assert fac_sciences in repo.get_all()
    repo.check_all()
