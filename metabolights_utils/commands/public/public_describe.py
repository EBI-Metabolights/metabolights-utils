from typing import Union

import click
from jsonpath_ng import parse

from metabolights_utils.commands.utils import print_study_model_summary
from metabolights_utils.models.parser.enums import ParserMessageType
from metabolights_utils.provider import definitions
from metabolights_utils.provider.ftp_repository import MetabolightsFtpRepository


@click.command(no_args_is_help=True, name="describe")
@click.option(
    "--local_path",
    "-p",
    default=definitions.default_local_repository_root_path,
    help="Local storage root path. Folder will be created if it does not exist.",
)
@click.option(
    "--ftp_server_url",
    "-f",
    default=definitions.default_ftp_server_url,
    help="FTP server URL where MetaboLights repository is hosted. ",
)
@click.option(
    "--ftp_root_directory",
    "-d",
    default=definitions.default_remote_repository_root_directory,
    help="MetaboLights study directory on FTP server URL. ",
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
    help="Downloads files and override current local copies. "
    "It is valid if there is no use_only_local option",
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
    "--use_study_model_cache",
    is_flag=True,
    default=True,
    help="Use only current local directory without connecting FTP server.",
)
@click.option(
    "--local_cache_path",
    "-c",
    default=definitions.default_local_repority_cache_path,
    help="Path to store cache files of FTP file indices, study models, etc.",
)
@click.argument("study_id")
@click.argument("jsonpath", required=False)
def public_describe(
    study_id: str = "",
    jsonpath: str = "",
    use_only_local: bool = False,
    local_path: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
    ftp_server_url: Union[None, str] = None,
    ftp_root_directory: Union[None, str] = None,
    override_local_files: bool = False,
    load_folder_index: bool = False,
    use_study_model_cache: bool = True,
):
    """
    View summary of any public study content. Run jsonpath expression to filter MetaboLights study model.

    study_id: MetaboLights study accession number (MTBLSxxxx).

    jsonpath (optional): jsonpath expression to filter study model.

    Print summary of study model if not specified.

        Example jsonpath expressions: "$.investigation.studies[0].title", "$.investigation.studies[0].study_protocols.protocols[*].name", "$.assays[*].*.table.columns[*]" - print column names

        Note: jsonpath expressions should be quoted with double quotes.
    """
    study_id = study_id.upper().strip()
    client = MetabolightsFtpRepository(
        ftp_server_url=ftp_server_url,
        remote_repository_root_directory=ftp_root_directory,
        local_storage_root_path=local_path,
        local_storage_cache_path=local_cache_path,
    )

    local_path = client.local_storage_root_path

    model, messages = client.load_study_model(
        study_id=study_id,
        local_path=local_path,
        use_only_local_path=use_only_local,
        override_local_files=override_local_files,
        load_folder_metadata=load_folder_index,
        use_study_model_cache=use_study_model_cache,
    )

    if (
        not model
        or not model.investigation
        or not model.investigation.studies
        or not model.investigation.studies[0]
    ):
        click.echo("Failure: There are parser error or invalid model.")
        exit(1)

    if jsonpath:
        try:
            json_data = model.model_dump()

            jsonpath_expr = parse(jsonpath)
            match_values = [match.value for match in jsonpath_expr.find(json_data)]
            if match_values:
                click.echo(
                    click.style(f"{study_id}: '{jsonpath}' search result:", fg="green")
                )
                if len(match_values) == 1:
                    click.echo(match_values[0])
                else:
                    for match_item in match_values:
                        click.echo(f"{match_item}")
            else:
                click.echo(click.style(f"{study_id}: '{jsonpath}' no match", fg="red"))
        except Exception as ex:
            click.echo(f"jsonpath '{jsonpath}' expression error: {str(ex)}")
            exit(1)
    else:
        if model.parser_messages:
            for file, messages in model.parser_messages.items():
                for message in messages:
                    if message.type in (
                        ParserMessageType.CRITICAL,
                        ParserMessageType.ERROR,
                    ):
                        click.echo(f"{study_id} {file}: {message.short}")
        click.echo(click.style("MetaboLights study model summary.", fg="green"))
        print_study_model_summary(model, log=click.echo)


if __name__ == "__main__":
    public_describe(["MTBLS1"])
