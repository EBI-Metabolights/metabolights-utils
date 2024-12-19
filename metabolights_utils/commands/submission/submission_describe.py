from typing import Union

import click
from jsonpath_ng import parse

from metabolights_utils.commands.utils import print_study_model_summary
from metabolights_utils.provider import definitions
from metabolights_utils.provider.submission_repository import (
    MetabolightsSubmissionRepository,
)


@click.command(no_args_is_help=True, name="describe")
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
    "--use_only_local",
    "-l",
    is_flag=True,
    default=False,
    help="Use only current local directory without connecting FTP server.",
)
@click.option(
    "--override_local_files",
    "-o",
    is_flag=True,
    default=False,
    help="Downloads files and override current local copies. It is valid if there is no use_only_local option",
)
@click.option(
    "--load_folder_index",
    "-i",
    is_flag=True,
    default=False,
    help="Create a folder index to store file descriptors on FTP seerver. "
    "It is valid if there is no use_only_local option.",
)
@click.option(
    "--local_cache_path",
    "-c",
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
@click.argument("jsonpath", required=False)
def submission_describe(
    study_id: str = "",
    jsonpath: str = "",
    use_only_local: bool = False,
    local_path: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
    rest_api_base_url: Union[None, str] = None,
    override_local_files: bool = False,
    credentials_file_path: str = "",
    load_folder_index: bool = False,
):
    """
    View summary of user's submitted (private) study. Run jsonpath expression to filter MetaboLights study model.

    study_id: MetaboLights study accession number (MTBLSxxxx).

    jsonpath (optional): jsonpath expression to filter study model. Print summary of study model if not specified.

        Example jsonpath expressions: "$.investigation.studies[0].title", "$.investigation.studies[0].study_protocols.protocols[*].name", "$.assays[*].*.table.columns[*]" - print column names

        Note: jsonpath expressions should be quoted with double quotes.
    """
    study_id = study_id.upper().strip()
    client = MetabolightsSubmissionRepository(
        local_storage_root_path=local_path,
        local_storage_cache_path=local_cache_path,
        rest_api_base_url=rest_api_base_url,
        credentials_file_path=credentials_file_path,
    )

    model, errors = client.load_study_model(
        study_id=study_id, use_only_local_path=use_only_local
    )

    if not model:
        if not errors:
            click.echo(f"{study_id}: {[x for x in errors]}")
        else:
            click.echo(f"{study_id}: load error.")
        exit(1)

        # error = True

    # if not error:

    if model and model.investigation and model.investigation.studies:
        if jsonpath:
            try:
                json_data = model.model_dump()

                jsonpath_expr = parse(jsonpath)
                match_values = [match.value for match in jsonpath_expr.find(json_data)]
                if match_values:
                    click.echo(
                        click.style(
                            f"{study_id}: '{jsonpath}' search result:", fg="green"
                        )
                    )
                    if len(match_values) == 1:
                        click.echo(match_values[0])
                    else:
                        for match_item in match_values:
                            click.echo(f"{match_item}")
                else:
                    click.echo(
                        click.style(f"{study_id}: '{jsonpath}' no match", fg="red")
                    )
            except Exception as ex:
                click.echo(f"jsonpath '{jsonpath}' expression error: {str(ex)}")
        else:
            click.echo(
                click.style("MetaboLights submission study model summary.", fg="green")
            )
            print_study_model_summary(model, log=click.echo)
    else:
        click.echo(f"{study_id} is not a valid or public study.")


if __name__ == "__main__":
    submission_describe(["MTBLS397", "-o"])
