from pathlib import Path
from typing import Union

import click

from metabolights_utils.provider import definitions
from metabolights_utils.provider.ftp.model import LocalDirectory
from metabolights_utils.provider.ftp_repository import MetabolightsFtpRepository
from metabolights_utils.provider.utils import is_metadata_filename_pattern


@click.command(name="download")
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
    "--override_local_files",
    "-o",
    is_flag=True,
    default=False,
    help="Downloads files and override current local copies.",
)
@click.argument("study_id")
@click.argument("file", required=False)
def public_download(
    study_id: Union[None, str] = None,
    file: Union[None, str] = None,
    local_path: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
    ftp_server_url: Union[None, str] = None,
    ftp_root_directory: Union[None, str] = None,
    override_local_files: bool = False,
):
    """
    Download study data and metadata files from MetaboLights FTP server.

    study_id: MetaboLights study accession number (MTBLSxxxx).

    file (optional): Relative file path in study folder. All ISA metadata files will be downloaded if not specified.
    """
    study_id = study_id.upper()
    client = MetabolightsFtpRepository(
        ftp_server_url=ftp_server_url,
        remote_repository_root_directory=ftp_root_directory,
        local_storage_root_path=local_path,
        local_storage_cache_path=local_cache_path,
    )
    is_metadata_file = is_metadata_filename_pattern(file)
    local_path = client.local_storage_root_path
    if not file or is_metadata_file:
        metadata_files = [file] if file else None
        result: LocalDirectory = client.download_study_metadata_files(
            study_id=study_id,
            local_path=local_path,
            metadata_files=metadata_files,
            override_local_files=override_local_files,
            delete_unlisted_metadata_files=False,
        )
    else:
        result: LocalDirectory = client.download_study_data_files(
            study_id=study_id,
            local_path=local_path,
            selected_data_files=[file] if file else None,
            override_local_files=override_local_files,
            skip_files=None,
            delete_unlisted_local_files=False,
            keep_local_files=None,
        )

    if result.success:
        if result.actions:
            local_study_path = Path(local_path) / Path(study_id)
            click.echo(
                click.style(f"Downloaded files on {local_study_path}", fg="green")
            )
            for item, action in result.actions.items():
                click.echo(f"{action}\t{item.replace(f'{study_id}/', '', 1)}")
        else:
            click.echo("There is no ISA metadata file to download.")
    else:
        click.echo(f"FTP response error: {result.message}")
        exit(1)
