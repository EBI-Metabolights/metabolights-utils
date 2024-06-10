import sys

import click

from metabolights_utils.commands.study.study_describe import study_describe
from metabolights_utils.commands.study.study_download import study_download
from metabolights_utils.commands.study.study_list import study_list
from metabolights_utils.commands.study.study_remove import study_remove
from metabolights_utils.commands.study.study_explain import study_explain


@click.group(name="study")
def study_cli():
    """Commands to use MetaboLights study data and ISA metadata files."""
    pass


study_cli.add_command(study_list)
study_cli.add_command(study_describe)
study_cli.add_command(study_download)
study_cli.add_command(study_remove)
study_cli.add_command(study_explain)
if __name__ == "__main__":
    if len(sys.argv) == 1:
        study_cli(["--help"])
    else:
        study_cli()
