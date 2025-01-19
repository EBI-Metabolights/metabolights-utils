import json
import logging
import os
from typing import Union

from metabolights_utils.commands.submission.model import (
    FtpLoginCredentials,
    LoginCredentials,
    RestApiCredentials,
)

logger = logging.getLogger(__name__)


def get_submission_private_ftp_credentials(
    credentials_file_path: str, private_ftp_url: str
) -> Union[None, FtpLoginCredentials]:
    credentials = get_submission_credentials(credentials_file_path)
    if credentials:
        if private_ftp_url in credentials.ftp_login:
            return credentials.ftp_login[private_ftp_url]
    return None


def get_submission_rest_api_credentials(
    credentials_file_path: str, rest_api_base_url: str
) -> Union[None, RestApiCredentials]:
    credentials = get_submission_credentials(credentials_file_path)
    if credentials:
        if rest_api_base_url in credentials.rest_api_credentials:
            return credentials.rest_api_credentials[rest_api_base_url]
    return None


def get_submission_credentials(credentials_file_path: str):
    credentials: Union[None, LoginCredentials] = None
    try:
        if os.path.exists(credentials_file_path):
            with open(credentials_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                credentials = LoginCredentials.model_validate(data)
    except Exception as ex:
        logger.exception("Error while loading %s", credentials_file_path, exc_info=ex)
    return credentials
