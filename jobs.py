#!/usr/bin/env python

"""
Cron-like scheduler
"""

import os
import time

import click
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

job_defaults = {
    'coalesce': False,
    'max_instances': 4
}
scheduler = BlockingScheduler(job_defaults=job_defaults)


@click.group()
def cli():
    pass


@cli.command()
def list():
    scheduler.print_jobs()


@cli.command()
def run():
    scheduler.start()


@scheduler.scheduled_job(CronTrigger(hour=1, minute=0, second=0))
def daily_reindex():
    os.system("./bin/flask reindex")


@scheduler.scheduled_job(CronTrigger(hour=6, minute=0, second=0))
def daily_sync():
    os.system("./bin/flask ldap_sync")
    os.system("./bin/flask syncbi")
    os.system("./bin/flask update_retard")


@scheduler.scheduled_job(CronTrigger(hour=0, minute=0, second=0))
def daily_recap():
    os.system("./bin/flask send_notifications daily")


@scheduler.scheduled_job(CronTrigger(day_of_week="thu", hour=0, minute=0, second=0))
def weekly_notif():
    os.system("./bin/flask send_notifications weekly")


@scheduler.scheduled_job(CronTrigger(day_of_week="tue", hour=0, minute=0, second=0))
def weekly_recap():
    os.system("./bin/flask send_recap")


if __name__ == "__main__":
    cli()
