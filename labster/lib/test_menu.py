from __future__ import annotations

from labster.domain2.services.roles import Role
from labster.lib.menu import Menu
from labster.test.test_web import login_as_dgrtt

MAIN = {
    "label": "Menu principal",
    "entries": [
        {"label": "Accueil", "endpoint": "main.home", "icon": "home"},
        {
            "label": "Tâches",
            "endpoint": "demandes.tasks",
            "icon": "check-square",
            "requires_role": {"recherche", "dgrtt"},
        },
        {
            "label": "Demandes en cours",
            "endpoint": "demandes.demandes",
            "icon": "briefcase",
            "requires_role": {"recherche", "dgrtt"},
        },
        {
            "label": "Demandes archivées",
            "endpoint": "demandes.archives",
            "icon": "graduation-cap",
            "requires_role": {"recherche", "dgrtt"},
        },
        {
            "label": "Questions & suggestions",
            "endpoint": "faq.home",
            "icon": "question",
        },
        {
            "label": "Statistiques",
            "endpoint": "bi.home",
            "icon": "chart-line",
            "requires_role": {
                Role.ADMIN_CENTRAL,
                Role.RESPONSABLE,
                # "alc",
                # "directeur",
                # "chef de bureau",
                # "gouvernance",
                # "direction dgrtt",
            },
        },
        {
            "label": 'Calculette "devis RH"',
            "endpoint": "demandes.calculette_devis_rh",
            "icon": "calculator",
        },
        {
            "label": 'Calculette "feuille de coûts"',
            "endpoint": "demandes.calculette_feuille_cout",
            "icon": "calculator",
        },
    ],
}


def test_menu_not_empty(client, db_session):
    login_as_dgrtt(client, db_session)
    menu = Menu(MAIN)
    assert not menu.is_empty()


def test_menu_serialize(client, db_session):
    login_as_dgrtt(client, db_session)
    menu = Menu(MAIN)
    dto = menu.asdict()
    assert isinstance(dto, dict)
