import json
import os
import random

from metabolights_utils.commands.submission.utils import (
    get_submission_credentials,
    get_submission_private_ftp_credentials,
    get_submission_rest_api_credentials,
)


def test_get_submission_credentials_01():
    result = get_submission_credentials(None)
    assert result is None


def test_get_submission_credentials_02():
    test_data = "invalid"
    credentials_file_path = (
        f"test-temp/mtbls_unit_test_{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        with open(credentials_file_path, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
        result = get_submission_credentials(credentials_file_path)
        assert result is None
    except Exception as ex:
        raise AssertionError(f"Error: {ex}")
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)


def test_get_submission_credentials_03():
    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
        "rest_api_credentials": {
            "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
        },
    }
    credentials_file_path = (
        f"test-temp/mtbls_unit_test_{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        with open(credentials_file_path, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
        result = get_submission_credentials(credentials_file_path)
        assert result
        assert result.ftp_login["ftp-private.ebi.ac.uk"].user_name == "x"
        assert result.ftp_login["ftp-private.ebi.ac.uk"].password == "y"
        assert (
            result.rest_api_credentials[
                "https://www.ebi.ac.uk/metabolights/ws"
            ].api_token
            == "z"
        )
    except Exception as ex:
        raise AssertionError(f"Error: {ex}")
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)


def test_get_submission_private_ftp_credentials_01():

    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
        "rest_api_credentials": {
            "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
        },
    }
    credentials_file_path = (
        f"test-temp/mtbls_unit_test_{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        with open(credentials_file_path, "w", encoding="utf-8") as f:
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
    except Exception as ex:
        raise AssertionError(f"Error: {ex}")
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)


def test_get_submission_rest_api_credentials_01():

    test_data = {
        "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
        "rest_api_credentials": {
            "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
        },
    }
    credentials_file_path = (
        f"test-temp/mtbls_unit_test_{random.randint(1000000, 9999999)}_tmp"
    )

    try:
        with open(credentials_file_path, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
        result = get_submission_rest_api_credentials(
            credentials_file_path, "https://www.ebi.ac.uk/metabolights/ws"
        )
        assert result
        assert result.api_token == "z"

        result = get_submission_rest_api_credentials(
            credentials_file_path, "https://www.ebi.ac.uk/metabolights/ws-invalid"
        )
        assert result is None
    except Exception as ex:
        raise AssertionError(f"Error: {ex}")
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)
