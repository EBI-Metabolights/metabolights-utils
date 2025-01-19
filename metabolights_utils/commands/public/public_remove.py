import os
import shutil
from typing import Union

import click

from metabolights_utils.provider import definitions


@click.command(name="remove", no_args_is_help=True)
@click.option(
    "--local_path",
    "-p",
    default=definitions.default_local_repository_root_path,
    help="Local storage root path. Folder will be created if it does not exist.",
)
@click.option(
    "--local_cache_path",
    "-c",
    default=definitions.default_local_repority_cache_path,
    help="Path to store cache files of FTP file indices, study models, etc.",
)
@click.argument("study_id")
def public_remove(
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
            click.echo(f"Study {study_id} folders are deleted.")
        else:
            click.echo(f"There is no folder for study {study_id}.")
    except Exception as ex:
        click.echo(f"Remove study {study_id} error: {ex}.")
        exit(1)


if __name__ == "__main__":
    public_remove(["MTBLS1"])
