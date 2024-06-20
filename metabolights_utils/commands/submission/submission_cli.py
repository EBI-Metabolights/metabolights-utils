import sys

import click

from metabolights_utils.commands.submission.submission_create_assay import (
    submission_create_assay,
)
from metabolights_utils.commands.submission.submission_delete_assay import (
    submission_delete_assay,
)
from metabolights_utils.commands.submission.submission_describe import (
    submission_describe,
)
from metabolights_utils.commands.submission.submission_download import (
    submission_download,
)
from metabolights_utils.commands.submission.submission_list import submission_list
from metabolights_utils.commands.submission.submission_login import submission_login
from metabolights_utils.commands.submission.submission_upload import submission_upload
from metabolights_utils.commands.submission.submission_validate import (
    submission_validate,
)


@click.group(name="submission")
def submission_cli():
    """Commands to use MetaboLights study submission REST API."""


submission_cli.add_command(submission_list)
submission_cli.add_command(submission_download)
submission_cli.add_command(submission_describe)
submission_cli.add_command(submission_login)
submission_cli.add_command(submission_upload)
submission_cli.add_command(submission_validate)
submission_cli.add_command(submission_create_assay)
submission_cli.add_command(submission_delete_assay)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        submission_cli(["--help"])
    else:
        submission_cli()
