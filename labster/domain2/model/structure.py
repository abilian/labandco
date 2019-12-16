"""De l'ancien annuaire:

260 {LL}Labo homologué (en cotutelle ou non)
 241 {SP}Service propre à l'UPMC
 238 {DO}Direction opérationnelle
 226 {SE}Service d'enseignement
  67 {C}Conseil ou commission d'université
  58 {SX}Service extérieur à l'UPMC
  58 {SS}Équipe, bureau, sous-service
  53 {LX}Laboratoire extérieur à l'UPMC
  21 {ED}Ecole Doctorale
  18 {IF}Institut Fédératif de Recherche
  16 {LF}Fédération de Recherche
  13 {UD}Unités extérieures diverses
   8 {LE}Équipe de recherche à l'UPMC
   8 {IO}Institut ou Observatoire
   8 {CU}Unité de Formation et de Recherche
   6 {SC}Service Commun
   3 {DI}Directoire d'université
   2 {CX}Ensemble de services ext UPMC
   1 {D}Decret
"""
from __future__ import annotations

import math
from abc import ABC, ABCMeta
from pprint import pformat
from typing import Any, Collection, List, Optional, Set
from uuid import uuid4

from attr import Factory, attrs

from labster.domain2.model.base import Repository

from .type_structure import ED, TypeStructure, get_type_structure


class StructureId(str):
    @staticmethod
    def new():
        return StructureId(uuid4())


@attrs(eq=False, order=False, repr=False, auto_attribs=True)
class Structure:
    # Cf. Slides de specs, page 2.
    """Un structure S comprend:

    • Un nom
    • Un acronyme (éventuellement vide)
    • Un type (cf. tableau page suivante)

    • Un champ LDAP, pour certaines structures réelles qui seront importées depuis l’annuaire
    • Une liste de structures parentes (ascendants directs)
    • Une liste de structures filles (descendantes directes)

    + Utilisateurs (générés par les rôles):

    • Une liste d’utilisateurs (dits « rattachés » si S est de type réel ou « participants » sinon)
    • Une R liste d’utilisateurs (rôle) dits « responsables de S
      » (typiquement R correspondant au rôle Directeur/Direction ;
      correspondant au rôle Président/Présidence dans le cas où
      S est Sorbonne Université et au rôle Doyen/Décanat dans le
      cas où S est l’une des trois facultés) qui sont :
        – Rattachés à S si S est réelle
        – Rattachés à l’un des laboratoires « enfants » si S est un regroupement de laboratoires
        – Rattachés au laboratoire dont ils font partie, si S est un département ou une équipe
    • Un utilisateur dit « signataire »
    • Une liste de gestionnaires
    • Une liste d’administrateurs
    """
    id: StructureId = StructureId("")
    old_id: Optional[int] = None
    active: bool = True

    #: Nom
    nom: str = ""

    #: Un acronyme (éventuellement vide)
    sigle: str = ""

    #: Un type (cf. tableau page suivante)
    type_name: str = ""

    #: Un champ LDAP, pour les structures réelles
    dn: str = ""

    #: Old DN, in case this comes from the old directory
    old_dn: str = ""

    #: Parents
    parents: Set[Structure] = Factory(set)

    #: Enfants
    children: Set[Structure] = Factory(set)

    #: Cache
    _depth: int = -1

    #: Propriétés additionnelles (non-spécifiées)
    permettre_reponse_directe: bool = False
    permettre_soummission_directe: bool = False

    email: str = Factory(str)

    def __attrs_post_init__(self):
        pass
        # self.check()

    def __str__(self):
        return f"<Structure type='{self.type_name}' nom='{self.nom}' id={id(self)}>"

    def __repr__(self):
        return str(self)

    @property
    def name(self) -> str:
        return self.nom

    @property
    def type(self) -> TypeStructure:
        return get_type_structure(self.type_name)

    @property
    def is_reelle(self) -> bool:
        return self.type.reel

    @property
    def sigle_ou_nom(self) -> str:
        return self.sigle or self.nom

    @property
    def parent(self) -> Optional[Structure]:
        if self.real_parents:
            return list(self.real_parents)[0]
        elif self.parents:
            return list(self.parents)[0]
        else:
            return None

    @property
    def real_parents(self) -> Collection[Structure]:
        return {p for p in self.parents if p.is_reelle}

    @property
    def virtual_parents(self) -> Collection[Structure]:
        return {p for p in self.parents if not p.is_reelle}

    def add_child(self, child: Structure):
        if not self.can_have_child(child):
            raise ValueError("Forbidden relation")

        child._depth = -1
        child.parents.add(self)
        self.children.add(child)

    def remove_child(self, child: Structure):
        child._depth = -1
        child.parents.remove(self)
        # self.children.remove(child)

    def can_have_child(self, other: Structure) -> bool:
        # if other.parents and other.type == EQ:
        #     return False

        my_type = self.type
        other_type = other.type

        return my_type.can_have_child_of_type(other_type)

    def add_parent(self, parent: Structure):
        parent.add_child(self)

    def remove_parent(self, parent: Structure):
        parent.remove_child(self)

    def can_have_parent(self, other: Structure) -> bool:
        return other.can_have_child(self)

    def delete(self):
        assert not self.children
        for parent in list(self.parents):
            self.remove_parent(parent)
        self.active = False

    @property
    def ancestors(self) -> List[Structure]:
        parent = self.parent
        if not parent:
            return []
        else:
            return [parent] + parent.ancestors

    @property
    def descendants(self) -> Set[Structure]:
        result = set()
        for child in self.children:
            result.add(child)
            result.update(child.descendants)
        return result

    @property
    def depth(self) -> int:
        if getattr(self, "_depth", -1) > -1:
            return self._depth
        parent = self.parent
        result = 0
        while True:
            if not parent:
                self._depth = result
                return result
            result += 1
            parent = parent.parent

    @property
    def path(self):
        return []

    def get_directeurs(self):
        # TODO
        return []

    def check(self):
        state = vars(self)
        try:
            for k, v in state.items():
                if isinstance(v, float) and math.isnan(v):
                    raise ValueError(f"Attribute {k} is NaN")

            self.type.full_check(self)

            if self.type == ED:
                assert len(self.parents) == 1
                assert self.parent.sigle == "IFD"

        except (AssertionError, ValueError):
            msg = f"Check failed on {self.sigle_ou_nom}. " + pformat(state)
            print(msg)
            raise


class StructureRepository(Repository, ABC, metaclass=ABCMeta):
    # @abstractmethod
    def put(self, structure: Structure):
        raise NotImplementedError

    # @abstractmethod
    def delete(self, structure: Structure):
        raise NotImplementedError

    # @abstractmethod
    def get_all(self) -> Set[Structure]:
        raise NotImplementedError

    # Generic (slow) implem
    def get_by(self, key: str, value: Any) -> Optional[Structure]:
        all_objects = self.get_all()
        for x in all_objects:
            if getattr(x, key) == value:
                return x
        return None

    def get_by_id(self, id: StructureId) -> Optional[Structure]:
        return self.get_by("id", id)

    def get_by_old_dn(self, old_dn: str) -> Optional[Structure]:
        return self.get_by("old_dn", old_dn)

    def get_by_dn(self, dn: str) -> Optional[Structure]:
        return self.get_by("dn", dn)

    def get_by_sigle(self, sigle: str) -> Optional[Structure]:
        return self.get_by("sigle", sigle)

    def get_by_old_id(self, old_id: int) -> Optional[Structure]:
        return self.get_by("old_id", old_id)

    def get_root(self) -> Structure:
        result = self.get_by_dn("ou=SU,ou=Affectations,dc=chapeau,dc=fr")
        assert result
        return result

    def check_all(self):
        for obj in self.get_all():
            obj.check()
