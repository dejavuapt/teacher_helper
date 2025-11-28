from app.bot.bot import main
import click
from app.settings import PROD

@click.group()
def cli():
    pass

@cli.command('run')
@click.option('--autoreload/--no-autoreload', 'R_flag', default=True, help="enable/disable autoreload logic. default is enabled")
def run(R_flag: bool):
    if R_flag and not PROD:
        # from app.utils.autoreload import autoreload
        # autoreload()
        click.echo("Watching...")
    click.echo("Run bot")
    # main()

entry_point = cli