from __future__ import annotations

from labster.lib.menu import Menu
from labster.test.test_web import login_as_dgrtt

MAIN = {
    "label": "Menu principal",
    "entries": [
        # Homes
        {"label": "Accueil", "to": "/", "icon": "home"},
        {"label": "Tâches", "to": "/tasks", "icon": "check-square",},
        {"label": "Mes demandes en cours", "to": "/demandes", "icon": "briefcase",},
        {"label": "Demandes archivées", "to": "/archives", "icon": "graduation-cap",},
        # Stuff
        {"label": "Questions & suggestions", "to": "/faq", "icon": "question"},
        {
            "label": 'Calculette "devis RH"',
            "to": "/calculette_rh",
            "icon": "calculator",
        },
        {
            "label": 'Calculette "feuille de coûts"',
            "endpoint": "main.calculette_feuille_cout",
            "icon": "calculator",
        },
    ],
}


def test_menu_not_empty(client, db_session):
    with login_as_dgrtt(client, db_session):
        menu = Menu(MAIN)
        assert not menu.is_empty()


def test_menu_serialize(client, db_session):
    with login_as_dgrtt(client, db_session):
        menu = Menu(MAIN)
        dto = menu.asdict()
        assert isinstance(dto, dict)
