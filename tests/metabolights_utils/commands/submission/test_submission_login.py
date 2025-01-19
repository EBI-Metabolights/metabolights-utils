import json
import random
from pathlib import Path

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from metabolights_utils.commands.submission.model import LoginCredentials
from metabolights_utils.commands.submission.submission_login import submission_login


@pytest.fixture
def credentials_file_path():
    credentials_file_path = Path(
        f"test-temp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )
    try:
        yield str(credentials_file_path)
    finally:
        credentials_file_path.unlink(missing_ok=True)


def test_submission_login_01(credentials_file_path: str):
    """
    Test the login command with a valid user credentials.
    """
    runner = CliRunner()

    assert not Path(credentials_file_path).exists()
    result = runner.invoke(
        submission_login,
        ["--credentials_file_path", credentials_file_path],
        input="x\ny\nz\n",
    )
    assert result.exit_code == 0
    assert "User credentials are updated successfully" in result.output
    assert Path(credentials_file_path).exists()


def test_submission_login_02(credentials_file_path: str):
    """
    Test overrides existing invalid credentials file
    """
    runner = CliRunner()

    with Path(credentials_file_path).open("w", encoding="utf-8") as f:
        json.dump("invalid", f)

    assert Path(credentials_file_path).exists()
    result = runner.invoke(
        submission_login,
        ["--credentials_file_path", credentials_file_path],
        input="x\ny\nz\n",
    )
    assert result.exit_code == 0
    assert "User credentials are updated successfully" in result.output
    assert Path(credentials_file_path).exists()


def test_submission_login_03(credentials_file_path: str):
    """
    Test update credentials.
    """
    runner = CliRunner()

    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "a", "password": "b"}},
        "rest_api_credentials": {
            "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "c"}
        },
    }
    with Path(credentials_file_path).open("w", encoding="utf-8") as f:
        json.dump(test_data, f)
    assert Path(credentials_file_path).exists()
    result = runner.invoke(
        submission_login,
        ["--credentials_file_path", credentials_file_path],
        input="x\ny\nz\n",
    )
    assert result.exit_code == 0
    assert "User credentials are updated successfully" in result.output
    assert Path(credentials_file_path).exists()
    with Path(credentials_file_path).open("r", encoding="utf-8") as f:
        data = json.load(f)
        credentials = LoginCredentials.model_validate(data)
        assert credentials.ftp_login["ftp-private.ebi.ac.uk"].user_name == "x"
        assert credentials.ftp_login["ftp-private.ebi.ac.uk"].password == "y"
        assert (
            credentials.rest_api_credentials[
                "https://www.ebi.ac.uk/metabolights/ws"
            ].api_token
            == "z"
        )


def test_submission_login_04(credentials_file_path: str):
    """
    Test the case when user enters empty values for all the fields
    """
    runner = CliRunner()
    credentials_file_path = (
        f"test-temp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )

    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
        "rest_api_credentials": {
            "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
        },
    }
    with Path(credentials_file_path).open("w", encoding="utf-8") as f:
        json.dump(test_data, f)
    assert Path(credentials_file_path).exists()
    result = runner.invoke(
        submission_login,
        ["--credentials_file_path", credentials_file_path],
        input="\n\n\n",
    )
    assert result.exit_code == 0
    assert "User credentials are not updated." in result.output
    assert Path(credentials_file_path).exists()
    with Path(credentials_file_path).open("r", encoding="utf-8") as f:
        data = json.load(f)
        credentials = LoginCredentials.model_validate(data)
        assert credentials.ftp_login["ftp-private.ebi.ac.uk"].user_name == "x"
        assert credentials.ftp_login["ftp-private.ebi.ac.uk"].password == "y"
        assert (
            credentials.rest_api_credentials[
                "https://www.ebi.ac.uk/metabolights/ws"
            ].api_token
            == "z"
        )


def test_submission_login_05(mocker: MockerFixture, credentials_file_path: str):
    """
    Test rollback if there is an error while updating credentials file
    """
    runner = CliRunner()

    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
        "rest_api_credentials": {
            "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
        },
    }
    with Path(credentials_file_path).open("w", encoding="utf-8") as f:
        json.dump(test_data, f)
    assert Path(credentials_file_path).exists()
    mocker.patch(
        "metabolights_utils.commands.submission.submission_login.json.dump",
        side_effect=Exception("Error"),
    )
    result = runner.invoke(
        submission_login,
        ["--credentials_file_path", credentials_file_path],
        input="a\nb\nc\n",
    )
    assert result.exit_code == 1
    assert "Error while login" in result.output
    assert Path(credentials_file_path).exists()
    with Path(credentials_file_path).open("r", encoding="utf-8") as f:
        data = json.load(f)
        credentials = LoginCredentials.model_validate(data)
        assert credentials.ftp_login["ftp-private.ebi.ac.uk"].user_name == "x"
        assert credentials.ftp_login["ftp-private.ebi.ac.uk"].password == "y"
        assert (
            credentials.rest_api_credentials[
                "https://www.ebi.ac.uk/metabolights/ws"
            ].api_token
            == "z"
        )


def test_submission_login_06(credentials_file_path: str):
    """
    Test add new ftp server and rest server url
    """
    runner = CliRunner()

    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
        "rest_api_credentials": {
            "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
        },
    }
    with Path(credentials_file_path).open("w", encoding="utf-8") as f:
        json.dump(test_data, f)
    assert Path(credentials_file_path).exists()
    rest_api_base_url = "test-url"
    ftp_server_url = "test-ftp-url"
    result = runner.invoke(
        submission_login,
        [
            "--credentials_file_path",
            credentials_file_path,
            "--rest_api_base_url",
            rest_api_base_url,
            "--ftp_server_url",
            ftp_server_url,
        ],
        input="a\nb\nc\n",
    )
    assert result.exit_code == 0
    assert "User credentials are updated successfully" in result.output
    assert Path(credentials_file_path).exists()
    with Path(credentials_file_path).open("r", encoding="utf-8") as f:
        data = json.load(f)
        credentials = LoginCredentials.model_validate(data)
        assert credentials.ftp_login["ftp-private.ebi.ac.uk"].user_name == "x"
        assert credentials.ftp_login[ftp_server_url].user_name == "a"
        assert credentials.ftp_login["ftp-private.ebi.ac.uk"].password == "y"
        assert credentials.ftp_login[ftp_server_url].password == "b"
        assert (
            credentials.rest_api_credentials[
                "https://www.ebi.ac.uk/metabolights/ws"
            ].api_token
            == "z"
        )
        assert credentials.rest_api_credentials[rest_api_base_url].api_token == "c"
