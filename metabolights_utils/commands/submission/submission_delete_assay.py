import os
from typing import Union

import click

from metabolights_utils.provider import definitions
from metabolights_utils.provider.submission_repository import (
    MetabolightsSubmissionRepository,
)


@click.command(no_args_is_help=True, name="delete-assay")
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
@click.option(
    "--save_audit_copy",
    "-o",
    is_flag=True,
    default=True,
    help="Save an audit folder before deleting assay file",
)
@click.argument("study_id")
@click.argument("assay_filename")
def submission_delete_assay(
    study_id: str = "",
    assay_filename: str = "",
    local_path: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
    rest_api_base_url: Union[None, str] = None,
    override_local_files: bool = False,
    credentials_file_path: str = "",
    save_audit_copy: bool = True,
):
    """
    Deletes a study assay file and referenced maf file.

    study_id: MetaboLights study accession number (MTBLSxxxx).
    assay_filename: Assay filename




    save_audit_copy (optional): creates an audit folder before deleting study

    """
    study_id = study_id.upper().strip()

    client = MetabolightsSubmissionRepository(
        local_storage_root_path=local_path,
        local_storage_cache_path=local_cache_path,
        rest_api_base_url=rest_api_base_url,
        credentials_file_path=credentials_file_path,
    )
    success, error = client.delete_assay(
        study_id=study_id,
        assay_filename=assay_filename,
        save_audit_copy=save_audit_copy,
    )
    if not success:
        click.echo(error)
        exit(1)
    else:
        click.echo(
            f"Assay file and related maf file are deleted for study : {study_id}: {assay_filename}"
        )

    result = client.download_submission_metadata_files(
        study_id=study_id,
        override_local_files=override_local_files,
        delete_unlisted_metadata_files=True,
    )
    study_path = os.path.join(client.local_storage_root_path, study_id)
    click.echo(f"Download submission study {study_id} on {study_path} status:")
    for item in result.actions:
        click.echo(f"  {result.actions[item]}\t{item}")


if __name__ == "__main__":
    submission_delete_assay(
        ["MTBLS9776", "a_MTBLS5397_LC-MS_positive_hilic_metabolite_profiling-1.txt"]
    )
