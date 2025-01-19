import os
from typing import Callable, List, Union

import click

from metabolights_utils.commands.utils import split_to_lines
from metabolights_utils.common import sort_by_study_id
from metabolights_utils.models.enums import GenericMessageType
from metabolights_utils.provider import definitions
from metabolights_utils.provider.ftp_repository import MetabolightsFtpRepository


@click.command(name="list")
@click.option(
    "--local_path",
    "-p",
    default=definitions.default_local_repository_root_path,
    help="Local storage root path. Folder will be created if it does not exist.",
)
@click.option(
    "--ftp_server_url",
    "-f",
    default=f"{definitions.default_ftp_server_url}",
    help="FTP server URL where MetaboLights repository is hosted. ",
)
@click.option(
    "--ftp_root_directory",
    "-d",
    default=f"{definitions.default_remote_repository_root_directory}",
    help="MetaboLights study directory on FTP server URL. ",
)
@click.option(
    "--local_cache_path",
    "-c",
    default=definitions.default_local_repority_cache_path,
    help="Path to store cache files of FTP file indices, study models, etc.",
)
@click.option(
    "--use_only_local",
    "-l",
    is_flag=True,
    default=False,
    help="Use only current local directory without connecting FTP server.",
)
@click.argument("study_id", required=False)
@click.argument("subdirectory", required=False)
def public_list(
    study_id: Union[None, str] = None,
    subdirectory: Union[None, str] = None,
    local_path: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
    ftp_server_url: Union[None, str] = None,
    ftp_root_directory: Union[None, str] = None,
    use_only_local: bool = False,
):
    """
    List studies and study folder content. It works for both local and remote FTP repository.

    study_id (optional): MetaboLights study accession number (MTBLSxxxx). List all studies if not specified.

    subdirectory (optional): Subdirectory of study to list its content. List the study root folder if not specified..
    """
    client = MetabolightsFtpRepository(
        ftp_server_url=ftp_server_url,
        remote_repository_root_directory=ftp_root_directory,
        local_storage_root_path=local_path,
        local_storage_cache_path=local_cache_path,
    )
    if use_only_local:
        search = client.local_storage_root_path
        if study_id:
            study_id = study_id.upper()
            search = os.path.join(client.local_storage_root_path, study_id)
            if subdirectory:
                search = os.path.join(search, subdirectory.strip("/"))
        if search == client.local_storage_root_path:
            studies = [x for x in os.listdir(search) if x.startswith("MTBLS")]
            studies.sort(key=sort_by_study_id)
            if studies:
                if len(studies) > 500:
                    print_list("Local public study", studies, click.echo_via_pager)
                else:
                    print_list("Local public study", studies, click.echo)
            else:
                click.echo("No public studies found on local storage.")
        else:
            items = os.listdir(search)
            for item in items:
                click.echo(f"\t{item}")
        return

    if study_id and study_id.strip():
        study_id = study_id.upper().strip()
        content_response = client.list_study_directory(
            study_id=study_id, subdirectory=subdirectory
        )
        if not content_response.success:
            click.echo(f"FTP response error: {content_response.message}")
            exit(1)
        for item in content_response.files:
            click.echo(f"\t{item}")

        for item in content_response.folders:
            click.echo(f"\t{item}")
    else:
        studies, messages = client.list_studies()
        error = False
        if messages:
            for message in messages:
                if message.type in (
                    GenericMessageType.CRITICAL,
                    GenericMessageType.ERROR,
                ):
                    click.echo(f"{message.short}")
                    error = True
        if error:
            exit(1)

        if len(studies) > 500:
            print_list("FTP Public study", studies, click.echo_via_pager)
        else:
            print_list("FTP Public study", studies, click.echo)


def print_list(label: str, items: List[str], log: Callable):
    item_str = ", ".join(items)

    lines = split_to_lines(item_str, sep=", ", join_term="\t", max_line_size=100)
    result = f"{label} count: {len(items)}\n\t" + "\n\t".join([x for x in lines])
    log(result)


if __name__ == "__main__":
    public_list()
