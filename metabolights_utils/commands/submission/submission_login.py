import json
import os
from typing import Union

import click

from metabolights_utils.commands.submission.model import (
    FtpLoginCredentials,
    LoginCredentials,
    RestApiCredentials,
)
from metabolights_utils.provider import definitions


@click.command(name="list")
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
    help=f"MetaboLights Rest API base URL.",
)
@click.option(
    "--ftp_server_url",
    "-f",
    default=definitions.default_private_ftp_server_url,
    help=f"FTP server URL where MetaboLights repository is hosted. ",
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
    Creates a file path to use connect private FTP server and MetaboLights Rest API.

    credentials_file_path (optional): File path to store user private FTP and MetaboLights Rest API credentials.

    """
    parent_directory = os.path.dirname(credentials_file_path)
    credentials: Union[None, LoginCredentials] = None
    initial: Union[None, LoginCredentials] = None
    try:
        if os.path.exists(credentials_file_path):
            with open(credentials_file_path, "r") as f:
                data = json.load(f)
                credentials = LoginCredentials.model_validate(data)
                initial = LoginCredentials.model_validate(data)
    except Exception as ex:
        click.echo("Error loading current credentials file. It will be overrided.")

    if not credentials:
        os.makedirs(parent_directory, exist_ok=True)
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
            json_data = credentials.model_dump()
            with open(credentials_file_path, "w") as f:
                json.dump(json_data, f, indent=4)
            click.echo("User credentials are updated succesfully.")
        else:
            click.echo("User credentials are not updated.")
    except Exception as ex:
        click.echo(f"Error while login: {str(ex)}")
        if initial:
            os.makedirs(parent_directory, exist_ok=True)
            json_data = initial.model_dump_json(indent=4)
            with open(credentials_file_path, "w") as f:
                json.dump(json_data, f, indent=4)


if __name__ == "__main__":
    submission_login()
