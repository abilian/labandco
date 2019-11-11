from __future__ import annotations

import structlog

from labster.di import injector
from labster.ldap2.ldif import get_ldif_file, parse_ldif_file, \
    update_users_from_records
from labster.ldap2.roles import RolesUpdater
from labster.persistence import Persistence

logger = structlog.get_logger()

persistence = injector.get(Persistence)


def sync_users():
    logger.info("## Synchronisation des utilisateurs avec le dump LDAP")
    ldif_file = get_ldif_file()
    new_records = parse_ldif_file(ldif_file)

    print(f"Nbre d'utilisateurs dans le LDIF: {len(new_records)}")
    update_users_from_records(new_records)

    logger.info("## Mise a jour des roles")
    roles_updater = RolesUpdater()
    roles_updater.update_roles()

    logger.debug("### Sauvegarde du repository")

    persistence.save()


def update_roles():
    roles_updater = RolesUpdater()
    roles_updater.update_roles()

    logger.debug("### Sauvegarde du repository")
    persistence.save()
