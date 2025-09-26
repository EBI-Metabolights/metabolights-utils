import click

from metabolights_utils import __version__
from metabolights_utils.commands.model.model_cli import model_cli
from metabolights_utils.commands.public.public_cli import public_cli
from metabolights_utils.commands.submission.submission_cli import submission_cli


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True
)
@click.version_option(__version__)
def cli():
    pass


cli.add_command(public_cli)
cli.add_command(submission_cli)
cli.add_command(model_cli)
