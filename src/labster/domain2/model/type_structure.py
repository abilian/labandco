from __future__ import annotations

from typing import TYPE_CHECKING

from attr import attrs

if TYPE_CHECKING:
    from labster.domain2.model.structure import Structure

void: frozenset[TypeStructure] = frozenset()


@attrs(hash=True, auto_attribs=True, frozen=True, str=False, repr=False)
class TypeStructure:
    name: str
    can_have_multiple_parents: bool
    reel: bool
    types_parents: frozenset[TypeStructure]

    def check(self, structure: Structure) -> bool:
        return structure.type == self

    def full_check(self, structure: Structure) -> None:
        msg = f"check failed on {structure}: {structure.type_name} != {self.name}"
        assert self.check(structure), msg

        parents = structure.parents
        for parent in parents:
            msg = (
                f"check failed on {structure}: "
                f"{parent.type_name} ∉ {self.types_parents}"
            )
            assert any(type.check(parent) for type in self.types_parents), msg

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return f"TypeStructure({self.name})"

    def can_have_parent_of_type(self, type: TypeStructure) -> bool:
        return type in self.types_parents

    def can_have_child_of_type(self, type: TypeStructure) -> bool:
        return type.can_have_parent_of_type(self)

    @property
    def id(self):
        for k, v in globals().items():
            if v == self:
                return k


def get_type_structure(name: str) -> TypeStructure:
    for obj in globals().values():
        if not isinstance(obj, TypeStructure):
            continue
        if obj.name.lower() == name.lower():
            return obj

    raise KeyError(name)


def get_type_structure_by_id(id: str) -> TypeStructure:
    for obj in globals().values():
        if not isinstance(obj, TypeStructure):
            continue
        if obj.id.lower() == id.lower():
            return obj

    raise KeyError(id)


f = frozenset

UN = TypeStructure("Université", False, True, void)
DU = TypeStructure("Direction universitaire", False, True, f({UN}))
SU = TypeStructure("Service universitaire", False, True, f({DU}))

FA = TypeStructure("Faculté", False, True, f({UN}))
DF = TypeStructure("Direction facultaire", False, True, f({FA}))
SF = TypeStructure("Service facultaire", False, True, f({DF}))

CO = TypeStructure("Composante", False, True, f({FA}))

CA = TypeStructure("Carnot", True, False, f({CO}))
LX = TypeStructure("Labex", True, False, f({CO}))
IN = TypeStructure("Institut", True, False, f({CO}))
GRC = TypeStructure("GRC", True, False, f({CO}))
INI = TypeStructure("Initiative", True, False, f({CO}))

ED = TypeStructure("École doctorale", False, True, f({DU}))
LA = TypeStructure("Laboratoire", False, True, f({CO, CA, LX, IN, GRC}))

DE = TypeStructure("Département", False, False, f({LA}))
EQ = TypeStructure("Équipe", False, False, f({LA, DE}))

ALL_TYPES = [UN, FA, DU, CO, SU, DF, LA, SF, ED, DE, EQ, CA, LX, IN, GRC, INI]
