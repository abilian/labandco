from __future__ import annotations


def mes_structures(user):
    roles = user.get_roles()
    structure = None
    for role in roles:
        if role.type == "Direction":
            structure = role.context
    return [structure] + structure.descendants()
