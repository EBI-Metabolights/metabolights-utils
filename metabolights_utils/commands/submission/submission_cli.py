import sys

import click

from metabolights_utils.commands.submission.submission_describe import (
    submission_describe,
)
from metabolights_utils.commands.submission.submission_download import (
    submission_download,
)
from metabolights_utils.commands.submission.submission_list import submission_list
from metabolights_utils.commands.submission.submission_login import submission_login
from metabolights_utils.commands.submission.submission_upload import submission_upload


@click.group(name="submission")
def submission_cli():
    """Commands to use MetaboLights study submission REST API."""
    pass


submission_cli.add_command(submission_list)
submission_cli.add_command(submission_download)
submission_cli.add_command(submission_describe)
submission_cli.add_command(submission_login)
submission_cli.add_command(submission_upload)
if __name__ == "__main__":
    if len(sys.argv) == 1:
        submission_cli(["--help"])
    else:
        submission_cli()
