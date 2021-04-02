from __future__ import annotations

from collections import OrderedDict
from typing import Dict, Text


class Group:
    def __init__(self, id, label, fields):
        self.id = id
        self.label = label
        self.fields = fields


class Groups:
    def __init__(self):
        self.dict = OrderedDict()  # type: Dict[Text, Group]

    def add_group(self, id, label, fields):
        self.dict[id] = Group(id, label, fields)

    def __getitem__(self, item):
        return self.dict[item]

    def __iter__(self):
        return iter(self.dict)


class Struct:
    """See: http://stackoverflow.com/questions/16327141/"""

    def __init__(self, **entries):
        self.__dict__.update(entries)
