#!/usr/bin/env python

"""Cron-like scheduler."""

import os
import sys

import click
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

job_defaults = {
    'coalesce': False,
    'max_instances': 4
}
scheduler = BlockingScheduler(job_defaults=job_defaults)

logger.remove(0)
logger.add(sys.stdout, format="{time} {level} {message}")


@click.group()
def cli():
    pass


@cli.command()
def list():
    scheduler.print_jobs()


@cli.command()
def run():
    logger.info("Starting job scheduler")
    scheduler.start()


def system(cmd: str):
    logger.info(cmd)
    status = os.system(cmd)
    logger.info(cmd + " exited with status {}", status)


@scheduler.scheduled_job(CronTrigger(hour=1, minute=0, second=0))
def daily_reindex():
    system("./bin/flask reindex")


@scheduler.scheduled_job(CronTrigger(hour=6, minute=0, second=0))
def daily_sync():
    system("./bin/flask ldap-sync")
    system("./bin/flask syncbi")
    system("./bin/flask update-retard")


@scheduler.scheduled_job(CronTrigger(hour=0, minute=0, second=0))
def daily_recap():
    system("./bin/flask send-notifications daily")


@scheduler.scheduled_job(CronTrigger(day_of_week="thu", hour=0, minute=0, second=0))
def weekly_notif():
    system("./bin/flask send-notifications weekly")


@scheduler.scheduled_job(CronTrigger(day_of_week="tue", hour=0, minute=0, second=0))
def weekly_recap():
    system("./bin/flask send-recap")


if __name__ == "__main__":
    cli()
