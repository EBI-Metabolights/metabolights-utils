import sys

import click

from metabolights_utils.commands.model.model_create import model_create
from metabolights_utils.commands.model.model_explain import model_explain


@click.group(name="model")
def model_cli():
    """Commands to explain MetaboLights study data model."""


model_cli.add_command(model_explain)
model_cli.add_command(model_create)
if __name__ == "__main__":
    if len(sys.argv) == 1:
        model_cli(["--help"])
    else:
        model_cli()
