import json
import os
import random

from click.testing import CliRunner
from pytest_mock import MockerFixture

from metabolights_utils.commands.submission.model import LoginCredentials
from metabolights_utils.commands.submission.submission_login import submission_login


def test_submission_login_01():
    """
    Test the login command with a valid user credentials.
    """
    runner = CliRunner()
    credentials_file_path = (
        f"/tmp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        assert not os.path.exists(credentials_file_path)
        result = runner.invoke(
            submission_login,
            ["--credentials_file_path", credentials_file_path],
            input="x\ny\nz\n",
        )
        assert result.exit_code == 0
        assert "User credentials are updated succesfully" in result.output
        assert os.path.exists(credentials_file_path)
    except Exception as ex:
        assert False, f"Error: {ex}"
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)


def test_submission_login_02():
    """
    Test overrides existing invalid credentials file
    """
    runner = CliRunner()
    credentials_file_path = (
        f"/tmp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        with open(credentials_file_path, "w") as f:
            json.dump("invalid", f)

        assert os.path.exists(credentials_file_path)
        result = runner.invoke(
            submission_login,
            ["--credentials_file_path", credentials_file_path],
            input="x\ny\nz\n",
        )
        assert result.exit_code == 0
        assert "User credentials are updated succesfully" in result.output
        assert os.path.exists(credentials_file_path)
    except Exception as ex:
        assert False, f"Error: {ex}"
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)


def test_submission_login_03():
    """
    Test update credentials.
    """
    runner = CliRunner()
    credentials_file_path = (
        f"/tmp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        test_data = {
            "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "a", "password": "b"}},
            "rest_api_credentials": {
                "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "c"}
            },
        }
        with open(credentials_file_path, "w") as f:
            json.dump(test_data, f)
        assert os.path.exists(credentials_file_path)
        result = runner.invoke(
            submission_login,
            ["--credentials_file_path", credentials_file_path],
            input="x\ny\nz\n",
        )
        assert result.exit_code == 0
        assert "User credentials are updated succesfully" in result.output
        assert os.path.exists(credentials_file_path)
        with open(credentials_file_path, "r") as f:
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
    except Exception as ex:
        assert False, f"Error: {ex}"
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)


def test_submission_login_04():
    """
    Test the case when user enters empty values for all the fields
    """
    runner = CliRunner()
    credentials_file_path = (
        f"/tmp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        test_data = {
            "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
            "rest_api_credentials": {
                "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
            },
        }
        with open(credentials_file_path, "w") as f:
            json.dump(test_data, f)
        assert os.path.exists(credentials_file_path)
        result = runner.invoke(
            submission_login,
            ["--credentials_file_path", credentials_file_path],
            input="\n\n\n",
        )
        assert result.exit_code == 0
        assert "User credentials are not updated." in result.output
        assert os.path.exists(credentials_file_path)
        with open(credentials_file_path, "r") as f:
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
    except Exception as ex:
        assert False, f"Error: {ex}"
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)


def test_submission_login_05(mocker: MockerFixture):
    """
    Test rollback if there is an error while updating credentials file
    """
    runner = CliRunner()
    credentials_file_path = (
        f"/tmp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        test_data = {
            "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
            "rest_api_credentials": {
                "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
            },
        }
        with open(credentials_file_path, "w") as f:
            json.dump(test_data, f)
        assert os.path.exists(credentials_file_path)
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
        assert os.path.exists(credentials_file_path)
        with open(credentials_file_path, "r") as f:
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
    except Exception as ex:
        assert False, f"Error: {ex}"
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)


def test_submission_login_06():
    """
    Test add new ftp server and rest server url
    """
    runner = CliRunner()
    credentials_file_path = (
        f"/tmp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        test_data = {
            "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
            "rest_api_credentials": {
                "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
            },
        }
        with open(credentials_file_path, "w") as f:
            json.dump(test_data, f)
        assert os.path.exists(credentials_file_path)
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
        assert "User credentials are updated succesfully" in result.output
        assert os.path.exists(credentials_file_path)
        with open(credentials_file_path, "r") as f:
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

    except Exception as ex:
        assert False, f"Error: {ex}"
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)
