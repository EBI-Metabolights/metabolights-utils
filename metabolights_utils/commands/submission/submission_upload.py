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
    help=f"MetaboLights study submission API base URL.",
)
@click.option(
    "--override_remote_files",
    "-o",
    is_flag=True,
    default=False,
    help=f"Downloads files and override current local copies. It is valid if there is no use_only_local option",
)
@click.option(
    "--local_cache_path",
    "-x",
    default=definitions.default_local_submission_cache_path,
    help=f"Path to store cache files of study submission file indices, study models, etc.",
)
@click.option(
    "--credentials_file_path",
    "-c",
    default=definitions.default_local_submission_credentials_file_path,
    help=f"Path to store cache files of study submission file indices, study models, etc.",
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
    Download submission study metadata files.

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
    result, error = client.upload_metadata_files(
        study_id=study_id,
        override_remote_files=override_remote_files,
        metadata_files=None,
    )
    click.echo(f"Upload submission study {study_id} :")
    # for item in result:
    #     click.echo(f"  {result.actions[item]}\t{item}")


if __name__ == "__main__":
    submission_upload(["MTBLS5397", "-o"])
