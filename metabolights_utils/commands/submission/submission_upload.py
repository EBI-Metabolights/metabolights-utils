from typing import Union

import click

from metabolights_utils.provider import definitions
from metabolights_utils.provider.submission_repository import (
    MetabolightsSubmissionRepository,
)


@click.command(no_args_is_help=True, name="upload")
@click.option(
    "--local_path",
    "-p",
    default=definitions.default_local_submission_root_path,
    help="Local storage root path. Folder will be created if it does not exist.",
)
@click.option(
    "--rest_api_base_url",
    "-u",
    default=definitions.default_rest_api_url,
    help="MetaboLights study submission API base URL.",
)
@click.option(
    "--override_remote_files",
    "-o",
    is_flag=True,
    default=False,
    help="Downloads files and override current local copies. It is valid if there is no use_only_local option",
)
@click.option(
    "--local_cache_path",
    "-x",
    default=definitions.default_local_submission_cache_path,
    help="Path to store cache files of study submission file indices, study models, etc.",
)
@click.option(
    "--credentials_file_path",
    "-c",
    default=definitions.default_local_submission_credentials_file_path,
    help="Path to store cache files of study submission file indices, study models, etc.",
)
@click.argument("study_id")
@click.argument("metadata_files", required=False)
def submission_upload(
    study_id: str = "",
    metadata_files: str = "",
    use_only_local: bool = False,
    local_path: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
    rest_api_base_url: Union[None, str] = None,
    override_remote_files: bool = False,
    credentials_file_path: str = "",
):
    """
    Uploads local metadata files to private FTP and start sync task to update study folder.

    study_id: MetaboLights study accession number (MTBLSxxxx).

    files (optional): files will be donwloaded. If not specified, downloads all ISA metadata files.
    """
    study_id = study_id.upper().strip()
    client = MetabolightsSubmissionRepository(
        local_storage_root_path=local_path,
        local_storage_cache_path=local_cache_path,
        rest_api_base_url=rest_api_base_url,
        credentials_file_path=credentials_file_path,
    )
    success, message = client.upload_metadata_files(
        study_id=study_id,
        override_remote_files=override_remote_files,
        metadata_files=None,
    )
    if success:
        click.echo(f"Upload private study {study_id} metadata files: Success")
        click.echo(message)
        
        success, error = client.sync_private_ftp_metadata_files(
            study_id=study_id, pool_period=10, retry=10
        )
        if success:
            click.echo(f"Sync private study {study_id} folder: Success")
        else:
            click.echo(f"Failure: Sync private study {study_id} folder: {error}")

    else:
        click.echo(f"Upload private study {study_id}: {message}")


if __name__ == "__main__":
    submission_upload(["MTBLS5397"])
