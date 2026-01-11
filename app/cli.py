import click
from app.settings import DEBUG, TG_BOT_TOKEN, DEBUG_HOST, DEBUG_PORT
from app.bot.bot import build_run
import toml
import logging

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command("run")
@click.option(
    "--debug/--no-debug",
    "is_debug",
    default=False,
    help="enable/disable autoreload logic. default is disable. also can set by DEBUG variable in env",
)
def run(is_debug: bool):
    data = toml.load("pyproject.toml")
    click.echo(f"Teachio version {data['project']['version']}")
    click.echo("Stop the bot with CTRL-BREAK or Ctrl-C.")
    if is_debug or DEBUG:
        try:
            from app.utils.autoreload import autoreload
            from app.utils.debugging import init_debugpy
            init_debugpy(DEBUG_HOST, int(DEBUG_PORT))
            click.echo(
                f"Debug server initialized. Hosted on: {DEBUG_HOST}:{DEBUG_PORT}"
            )

            click.echo("File watcher initialized. Tracking changes in .py files.")
            autoreload(build_run, token=TG_BOT_TOKEN)
        except ModuleNotFoundError as e:
            click.secho(f"{str(e)}", fg="red")
            click.echo("Run without debugging")
            build_run(TG_BOT_TOKEN)
    else:
        build_run(TG_BOT_TOKEN)


entry_point = cli
