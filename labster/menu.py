from __future__ import annotations

from labster.domain2.services.roles import Role
from labster.lib.menu import Menu
from labster.rbac import can_view_stats

MAIN = {
    "label": "Menu principal",
    "entries": [
        # Homes
        {"label": "Accueil", "to": "/", "icon": "home"},
        {
            "label": "Tâches",
            "to": "/tasks",
            "icon": "check-square",
        },
        {
            "label": "Mes demandes en cours",
            "to": "/demandes",
            "icon": "briefcase",
        },
        {
            "label": "Demandes archivées",
            "to": "/archives",
            "icon": "graduation-cap",
        },
        # Stuff
        {"label": "Questions & suggestions", "to": "/faq", "icon": "question"},
        {
            "label": "Statistiques",
            "to": "/bi",
            "icon": "chart-line",
            "precondition": can_view_stats,
        },
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
        # {"label": "Home", "icon": "home", "requires_role": {"alc"},},
        # {"label": "Tableau de bord", "icon": "chart-line", "requires_role": {"alc"},},
        {
            "label": "Gérer la FAQ",
            "icon": "question",
            "to": "/admin/faq",
            "requires_role": {Role.ADMIN_CENTRAL, Role.FAQ_EDITOR},
        },
        {
            "label": "Config",
            "icon": "sliders-h",
            "to": "/admin/constants",
            "requires_role": {"alc"},
        },
        {
            "label": "Rôles globaux",
            "icon": "lock",
            "to": "/admin/roles",
            "requires_role": {"alc"},
        },
        # {
        #     "label": "Financeurs",
        #     "icon": "euro-sign",
        #     # "endpoint": "admin2.financeurs",
        #     "requires_role": {"alc"},
        # },
    ],
}


def get_menu(user):
    menus = [Menu(MAIN), Menu(ANNUAIRES), Menu(ADMIN)]

    return [m for m in menus if not m.is_empty()]
