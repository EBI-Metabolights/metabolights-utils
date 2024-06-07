import os
import shutil
from typing import Dict, List, Union

import click

from metabolights_utils.commands.utils import print_study_model_summary, split_to_lines
from metabolights_utils.models.parser.enums import ParserMessageType
from metabolights_utils.provider import definitions
from metabolights_utils.provider.ftp_repository import MetabolightsFtpRepository


@click.command(name="remove", no_args_is_help=True)
@click.option(
    "--local_path",
    "-p",
    default=definitions.default_local_repority_root_path,
    help="Local storage root path. Folder will be created if it does not exist.",
)
@click.option(
    "--local_cache_path",
    "-c",
    default=definitions.default_local_repority_cache_path,
    help=f"Path to store cache files of FTP file indices, study models, etc.",
)
@click.argument("study_id")
def study_remove(
    study_id: Union[None, str] = None,
    local_path: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
):
    """
    Delete local study data and metadata files.

    study_id: MetaboLights study accession number (MTBLSxxxx).
    """

    study_id = study_id.upper()
    try:
        data_path = os.path.join(local_path, study_id)
        cache_path = os.path.join(local_cache_path, study_id)
        deleted = False
        for folder in (data_path, cache_path):
            if os.path.exists(folder):
                shutil.rmtree(folder)
                deleted = True
        if deleted:
            click.echo(f"Study  {study_id} folders are deleted.")
        else:
            click.echo(f"There is no folder for study {study_id}.")
    except Exception as ex:
        click.echo(f"Remove study {study_id} error: {ex}.")
        exit(1)


if __name__ == "__main__":
    study_remove()
