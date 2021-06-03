from __future__ import annotations

import glob
import os
import sys

import structlog

from .ldif import parse_ldif_file, update_users_from_records
from .roles import RolesUpdater

logger = structlog.get_logger()


def sync_users():
    logger.info("## Synchronisation des utilisateurs avec le dump LDAP")
    ldif_file = get_ldif_file()
    new_records = parse_ldif_file(ldif_file)

    print(f"Nbre d'utilisateurs dans le LDIF: {len(new_records)}")
    update_users_from_records(new_records)

    logger.info("## Mise a jour des roles")
    update_roles()


def get_ldif_file():
    files = glob.glob("annuaire/export-Lab-Co-Dev*.ldif")
    if not files:
        files = glob.glob("annuaire/export-Lab-Co.*.ldif")
    files.sort()
    if not files:
        logger.error("Error: not LDIF file found in annuaire/")
        sys.exit(-1)
    ldif_file = files[-1]

    # Remove old files
    for file_to_remove in files[0:-1]:
        logger.info(f"removing {file_to_remove}")
        os.unlink(file_to_remove)

    return ldif_file


def update_roles(max=0):
    roles_updater = RolesUpdater()
    roles_updater.update_roles(max)
