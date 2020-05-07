from __future__ import annotations


def get_form(
    require_note=False,
    ask_for_revalidation=False,
    with_no_infolab=False,
    with_no_eotp=False,
):
    form = [
        {"name": "note", "label": "Note", "type": "textarea", "required": require_note},
    ]

    if ask_for_revalidation:
        form.append(
            {
                "name": "resoumission",
                "label": "Redemander validation par la hiérarchie",
                "type": "bool",
                "required": False,
            },
        )

    if with_no_infolab:
        form.append(
            {
                "name": "no_infolab",
                "label": "N° Infolab / Référence",
                "type": "text",
                "required": True,
            },
        )
    if with_no_eotp:
        form.append(
            {"name": "no_eotp", "label": "N° EOTP", "type": "text", "required": True},
        )

    return form
