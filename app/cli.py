from app.bot.bot import main
import click
from app.settings import PROD
import sys, os

@click.group()
def cli():
    pass

@cli.command('run')
@click.option('--autoreload/--no-autoreload', 'R_flag', default=True, help="enable/disable autoreload logic. default is enabled")
def run(R_flag: bool):
    if R_flag and not PROD:
        from app.utils.autoreload import autoreload
        autoreload(lambda: click.echo("Watch...."))
        # executable_path: str = os.path.join(os.getcwd(), 'teachio')
        # click.echo(f"Run bot {sys.executable}, {sys.argv}")
        # os.execv(sys.argv[0], sys.argv[:])
        # os.execv(executable_path, [*sys.argv[:], '--no-autoreload'])
        # after execv not work enything
    click.echo(f"Run bot {sys.executable}, {sys.argv}")
    # main()

entry_point = cli