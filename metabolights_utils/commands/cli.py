import sys

import click

from metabolights_utils.commands.study.study_cli import study_cli


@click.group()
def cli():
    pass


cli.add_command(study_cli)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        cli(["--help"])
    else:
        cli()
