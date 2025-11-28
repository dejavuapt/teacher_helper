import click
from app.settings import PROD, TG_BOT_TOKEN
from app.bot.bot import build_run
import sys, os
import toml
import logging

logger = logging.getLogger(__name__)

@click.group()
def cli():
    pass

@cli.command('run')
@click.option('--autoreload/--no-autoreload', 'R_flag', default=True, help="enable/disable autoreload logic. default is enabled")
def run(R_flag: bool):
    data = toml.load('pyproject.toml')
    click.echo(f"Teachio version {data['project']['version']}")
    click.echo("Stop the bot with CTRL-BREAK or Ctrl-C.")
    if R_flag and not PROD:
        from app.utils.autoreload import autoreload
        logger.info("File watcher initialized. Tracking changes in .py files.")
        autoreload(build_run, token=TG_BOT_TOKEN)
    else:
        build_run(TG_BOT_TOKEN)

entry_point = cli