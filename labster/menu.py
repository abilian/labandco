from __future__ import annotations

from flask import g

from labster.lib.menu import Menu

MAIN = {
    "label": "Menu principal",
    "entries": [
        # Homes
        {"label": "Accueil", "to": "/", "icon": "home"},
        {
            "label": "Tâches",
            "to": "/tasks",
            "icon": "check-square",
            "requires_role": {"recherche", "dgrtt"},
        },
        {
            "label": "Mes demandes en cours",
            "to": "/demandes",
            "icon": "briefcase",
            "requires_role": {"recherche", "dgrtt"},
        },
        {
            "label": "Demandes archivées",
            "to": "/archives",
            "icon": "graduation-cap",
            "requires_role": {"recherche", "dgrtt"},
        },
        # Stuff
        {"label": "Questions & suggestions", "to": "/faq", "icon": "question"},
        {
            "label": "Statistiques",
            # "endpoint": "bi.home",
            "icon": "chart-line",
            "requires_role": {
                "alc",
                "directeur",
                "chef de bureau",
                "gouvernance",
                "direction dgrtt",
            },
        },
        {
            "label": 'Calculette "devis RH"',
            # "endpoint": "demandes.calculette_devis_rh",
            "icon": "calculator",
        },
        {
            "label": 'Calculette "feuille de coûts"',
            # "endpoint": "demandes.calculette_feuille_cout",
            "icon": "calculator",
        },
    ],
}

ANNUAIRES = {
    "label": "Annuaires",
    "entries": [
        {"label": "Structures", "to": "/annuaire/structures", "icon": "sitemap"},
        {"label": "Utilisateurs", "to": "/annuaire/users", "icon": "user"},
        {
            "label": "Contacts Lab&Co",
            "to": "/contacts",
            "icon": "arrows-alt",
            "requires_role": {"alc"},
        },
    ],
}

ADMIN = {
    "label": "Administration",
    "entries": [
        {
            "label": "Home",
            "icon": "home",
            # "endpoint": "admin2.home",
            "requires_role": {"alc"},
        },
        {
            "label": "Tableau de bord",
            "icon": "chart-line",
            # "endpoint": "admin2.dashboard",
            "requires_role": {"alc"},
        },
        # {
        #     "label": "Mapping DR&I",
        #     "icon": "arrows-alt",
        #     "endpoint": "admin2.mapping_dgrtt",
        #     "requires_role": {"alc"},
        # },
        {
            "label": "Gérer la FAQ",
            "icon": "question",
            # "endpoint": "admin2.faq_home",
            "requires_role": {"alc"},
            # FIXME: fix later
            # "requires_role": {Role.ADMIN_CENTRAL, Role.FAQ_EDITOR},
        },
        {
            "label": "Config",
            "icon": "sliders-h",
            # "endpoint": "admin2.constants",
            "requires_role": {"alc"},
        },
        {
            "label": "Financeurs",
            "icon": "euro-sign",
            # "endpoint": "admin2.financeurs",
            "requires_role": {"alc"},
        },
    ],
}


def inject_menu():
    user = g.current_user

    if not user:
        g.menu = []
        return

    menus = [Menu(MAIN), Menu(ANNUAIRES), Menu(ADMIN)]

    g.menu = [m for m in menus if not m.is_empty()]
