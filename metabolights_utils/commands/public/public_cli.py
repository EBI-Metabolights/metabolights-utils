import sys

import click

from metabolights_utils.commands.public.public_describe import public_describe
from metabolights_utils.commands.public.public_download import public_download
from metabolights_utils.commands.public.public_list import public_list
from metabolights_utils.commands.public.public_remove import public_remove


@click.group(name="public")
def public_cli():
    """Commands to use MetaboLights public study data and ISA metadata files."""
    pass


public_cli.add_command(public_list)
public_cli.add_command(public_describe)
public_cli.add_command(public_download)
public_cli.add_command(public_remove)
if __name__ == "__main__":
    if len(sys.argv) == 1:
        public_cli(["--help"])
    else:
        public_cli()
