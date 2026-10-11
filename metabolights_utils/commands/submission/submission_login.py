import json
import os
import sys
from typing import Union

import click

from metabolights_utils.commands.submission.model import (
    FtpLoginCredentials,
    LoginCredentials,
    RestApiCredentials,
)
from metabolights_utils.provider import definitions


def write_credentials_file(
    credentials_file_path: str,
    credentials: Union[LoginCredentials, None] = None,
    json_text: Union[str, None] = None,
):
    parent_directory = os.path.dirname(credentials_file_path)
    if parent_directory and not os.path.exists(parent_directory):
        os.makedirs(parent_directory, mode=0o700, exist_ok=True)
        os.chmod(parent_directory, 0o700)

    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(credentials_file_path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if json_text is not None:
                f.write(json_text)
            else:
                json.dump(credentials.model_dump(), f, indent=4)
    finally:
        os.chmod(credentials_file_path, 0o600)


@click.command(name="login")
@click.option(
    "--credentials_file_path",
    "-c",
    default=definitions.default_local_submission_credentials_file_path,
    help="Credentials file path.",
)
@click.option(
    "--rest_api_base_url",
    "-a",
    default=f"{definitions.default_rest_api_url}",
    help="MetaboLights Rest API base URL.",
)
@click.option(
    "--ftp_server_url",
    "-f",
    default=definitions.default_private_ftp_server_url,
    help="FTP server URL where MetaboLights repository is hosted. ",
)
@click.option("--ftp_user", prompt=True, default="", hide_input=False)
@click.option("--ftp_user_password", prompt=True, default="", hide_input=True)
@click.option("--api_token", prompt=True, default="", hide_input=True)
def submission_login(
    credentials_file_path: str = "",
    rest_api_base_url="",
    ftp_server_url: str = "",
    ftp_user: str = "",
    ftp_user_password: str = "",
    api_token: str = "",
):
    """
    Creates a file to connect private FTP server and MetaboLights Rest API.

    credentials_file_path (optional): File path to store user private FTP and MetaboLights Rest API credentials.

    """
    parent_directory = os.path.dirname(credentials_file_path)
    credentials: Union[None, LoginCredentials] = None
    initial: Union[None, LoginCredentials] = None
    try:
        if os.path.exists(credentials_file_path):
            with open(credentials_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                credentials = LoginCredentials.model_validate(data)
                initial = LoginCredentials.model_validate(data)
    except Exception as ex:
        click.echo(
            f"Error loading current credentials file. It will be overrided: {str(ex)}"
        )

    if not credentials:
        if parent_directory and not os.path.exists(parent_directory):
            os.makedirs(parent_directory, mode=0o700, exist_ok=True)
            os.chmod(parent_directory, 0o700)
        credentials = LoginCredentials()
    try:
        if ftp_user and ftp_user_password:
            if ftp_server_url not in credentials.ftp_login:
                credentials.ftp_login[ftp_server_url] = FtpLoginCredentials()

            detail = credentials.ftp_login[ftp_server_url]
            detail.user_name = ftp_user
            detail.password = ftp_user_password

        if api_token:
            if rest_api_base_url not in credentials.rest_api_credentials:
                credentials.rest_api_credentials[rest_api_base_url] = (
                    RestApiCredentials()
                )
            detail = credentials.rest_api_credentials[rest_api_base_url]
            detail.api_token = api_token

        if api_token or ftp_user or ftp_user_password:
            write_credentials_file(credentials_file_path, credentials=credentials)
            click.echo("User credentials are updated successfully.")
        else:
            click.echo("User credentials are not updated.")
    except Exception as ex:
        click.echo(f"Error while login: {str(ex)}")
        if initial:
            json_data = initial.model_dump_json(indent=4)
            write_credentials_file(credentials_file_path, json_text=json_data)
        sys.exit(1)


if __name__ == "__main__":
    submission_login()
