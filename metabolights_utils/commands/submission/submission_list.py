from typing import Union

import click

from metabolights_utils.commands.submission.model import (
    StudyResponse,
    SubmittedStudySummary,
)
from metabolights_utils.commands.utils import convert_html_to_plain_text, split_to_lines
from metabolights_utils.provider import definitions
from metabolights_utils.provider.submission_repository import (
    MetabolightsSubmissionRepository,
)


def print_submitted_study(study: SubmittedStudySummary, log):
    log("-" * 120)
    log(f"{study.accession}: {study.title}")
    public_date = study.release_date
    submission_date = study.created_date
    lines = split_to_lines(convert_html_to_plain_text(study.description))
    for line in lines:
        log(f"\t{line}")
    log(f"\nRelease Date\t: {public_date}\nSubmission Date\t: {submission_date}")


@click.command(name="list")
@click.option(
    "--local_path",
    "-p",
    default=definitions.default_local_submission_root_path,
    help="Local storage root path. Folder will be created if it does not exist.",
)
@click.option(
    "--rest_api_base_url",
    "-f",
    default=f"{definitions.default_rest_api_url}",
    help="MetaboLights Rest API base URL.",
)
@click.option(
    "--local_cache_path",
    "-x",
    default=definitions.default_local_repority_cache_path,
    help="Path to store cache files of submission study folder indices, study models, etc.",
)
@click.option(
    "--use_only_local",
    "-l",
    is_flag=True,
    default=False,
    help="Use only current local directory without REST API.",
)
@click.option(
    "--timeout",
    "-t",
    default=10,
    type=int,
    help="Rest API response timeout.",
)
@click.option(
    "--credentials_file_path",
    "-c",
    default=definitions.default_local_submission_credentials_file_path,
    help="Credentials file path.",
)
@click.argument("study_id", required=False)
@click.argument("subdirectory", required=False)
def submission_list(
    study_id: Union[None, str] = None,
    subdirectory: Union[None, str] = None,
    local_path: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
    rest_api_base_url: Union[None, str] = None,
    use_only_local: bool = False,
    timeout: int = 10,
    credentials_file_path: str = "",
):
    """
    List submitted studies and study folder content. It works for both local and Rest API.

    study_id (optional): MetaboLights study accession number (MTBLSxxxx). List all studies submitted by user, if not specified.

    subdirectory (optional): Subdirectory of submitted study folder to list its content. List the study root folder if not specified..
    """
    client = MetabolightsSubmissionRepository(
        local_storage_root_path=local_path,
        local_storage_cache_path=local_cache_path,
        rest_api_base_url=rest_api_base_url,
        credentials_file_path=credentials_file_path,
    )

    if not study_id:
        studies_data, error = client.list_studies(timeout=timeout)
        if studies_data:
            studies = studies_data.data.copy()
            studies.sort(key=lambda x: x.updated)
            click.echo("Submitted studies by user:")
            for item in studies:
                print_submitted_study(item, log=click.echo)
            click.echo("-" * 120)
        else:
            click.echo(error)
    else:
        study_id = study_id.upper().strip()

        data, error = client.list_study_directory(
            study_id=study_id, subdirectory=subdirectory, timeout=timeout
        )
        if data:
            studies_response = StudyResponse.model_validate(data)
            studies = studies_response.study.copy()
            studies.sort(key=lambda x: x.file)
            search_path = study_id if not subdirectory else f"{study_id}/{subdirectory}"
            click.echo(f"Submission Study Folder: {search_path}")
            for item in studies:
                click.echo(f"  {item.created_at}\t{item.file}")
        else:
            click.echo(error)


if __name__ == "__main__":
    submission_list()
