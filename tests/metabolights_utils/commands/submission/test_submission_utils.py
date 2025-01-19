import json
import random
from pathlib import Path

import pytest

from metabolights_utils.commands.submission.utils import (
    get_submission_credentials,
    get_submission_private_ftp_credentials,
    get_submission_rest_api_credentials,
)


@pytest.fixture
def credentials_file_path():
    credentials_file_path = Path(
        f"test-temp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )
    try:
        yield str(credentials_file_path)
    finally:
        credentials_file_path.unlink(missing_ok=True)


def test_get_submission_credentials_01():
    result = get_submission_credentials(None)
    assert result is None


def test_get_submission_credentials_02(credentials_file_path: str):
    test_data = "invalid"

    with Path(credentials_file_path).open("w", encoding="utf-8") as f:
        json.dump(test_data, f)
    result = get_submission_credentials(credentials_file_path)
    assert result is None


def test_get_submission_credentials_03(credentials_file_path: str):
    resource = "https://www.ebi.ac.uk/metabolights/ws"
    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
        "rest_api_credentials": {resource: {"api_token": "z"}},
    }

    with Path(credentials_file_path).open("w", encoding="utf-8") as f:
        json.dump(test_data, f)
    result = get_submission_credentials(credentials_file_path)
    assert result
    assert result.ftp_login["ftp-private.ebi.ac.uk"].user_name == "x"
    assert result.ftp_login["ftp-private.ebi.ac.uk"].password == "y"
    assert result.rest_api_credentials[resource].api_token == "z"


def test_get_submission_private_ftp_credentials_01(credentials_file_path: str):
    resource = "https://www.ebi.ac.uk/metabolights/ws"
    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
        "rest_api_credentials": {resource: {"api_token": "z"}},
    }

    with Path(credentials_file_path).open("w", encoding="utf-8") as f:
        json.dump(test_data, f)
    result = get_submission_private_ftp_credentials(
        credentials_file_path, "ftp-private.ebi.ac.uk"
    )
    assert result
    assert result.user_name == "x"
    assert result.password == "y"

    result = get_submission_private_ftp_credentials(
        credentials_file_path, "ftp-private.ebi.ac.uk-invalid"
    )
    assert result is None


def test_get_submission_rest_api_credentials_01(credentials_file_path: str):
    resource = "https://www.ebi.ac.uk/metabolights/ws"
    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
        "rest_api_credentials": {resource: {"api_token": "z"}},
    }
    with Path(credentials_file_path).open("w", encoding="utf-8") as f:
        json.dump(test_data, f)
    result = get_submission_rest_api_credentials(credentials_file_path, resource)
    assert result
    assert result.api_token == "z"

    result = get_submission_rest_api_credentials(
        credentials_file_path, "https://www.ebi.ac.uk/metabolights/ws-invalid"
    )
    assert result is None
