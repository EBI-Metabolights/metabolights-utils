import os
from typing import Union

import click

from metabolights_utils.provider import definitions
from metabolights_utils.provider.submission_repository import (
    MetabolightsSubmissionRepository,
)


@click.command(no_args_is_help=True, name="validate")
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
    "--validation_file_path",
    "-v",
    help="Path to store validation file.",
)
@click.argument("study_id")
def submission_validate(
    study_id: str = "",
    rest_api_base_url: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
    validation_file_path: bool = False,
    credentials_file_path: str = "",
):
    """
    Validate submitted study and save validation report on local storage.

    study_id: MetaboLights study accession number (MTBLSxxxx).

    """
    if not validation_file_path:
        validation_file_path = os.path.join(
            local_cache_path, study_id, f"{study_id}_validation_report.tsv"
        )
    validation_file_path = os.path.realpath(validation_file_path)
    dir_name = os.path.dirname(validation_file_path)
    os.makedirs(dir_name, exist_ok=True)

    study_id = study_id.upper().strip()
    client = MetabolightsSubmissionRepository(
        local_storage_cache_path=local_cache_path,
        rest_api_base_url=rest_api_base_url,
        credentials_file_path=credentials_file_path,
    )
    success, error = client.validate_study(
        study_id,
        validation_file_path=validation_file_path,
    )

    if success:
        with open(validation_file_path, "r", encoding="utf-8") as f:
            validation_report = f.readlines()
            for line in validation_report:
                click.echo(line.strip())
        click.echo(f"Validation report is saved as {validation_file_path}")
    else:
        click.echo(f"Validate study {study_id} error: {error}.")
        exit(1)


if __name__ == "__main__":
    submission_validate(["MTBLS5397"])
