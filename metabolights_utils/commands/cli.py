import sys

import click

from metabolights_utils.commands.model.model_cli import model_cli
from metabolights_utils.commands.public.public_cli import public_cli
from metabolights_utils.commands.submission.submission_cli import submission_cli


@click.group()
def cli():
    pass


cli.add_command(public_cli)
cli.add_command(submission_cli)
cli.add_command(model_cli)

if __name__ == "__main__":
    if len(sys.argv) == 0:
        cli(["--help"])
    else:
        cli()
