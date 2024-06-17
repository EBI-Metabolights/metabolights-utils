import json
import os
import random
import shutil
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel
from pytest_mock import MockerFixture

from metabolights_utils.commands.submission.model import (
    ResponseFileDescriptor,
    StudyResponse,
)
from metabolights_utils.models.metabolights.model import MetabolightsStudyModel
from metabolights_utils.provider.ftp.model import LocalDirectory
from metabolights_utils.provider.submission_repository import (
    MetabolightsSubmissionRepository,
)


def test_submission_provider_01():
    provider = MetabolightsSubmissionRepository()
    assert provider.credentials_file_path


class MockHttpResponse(BaseModel):
    status_code: int = 200
    text: str = ""
    json_data: str = {}


def test_create_assay_01(mocker: MockerFixture):
    credentials_file_path = (
        f"/tmp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )
    local_storage_root_path = (
        f"/tmp/mtbls_unit_test_local{random.randint(1000000, 9999999)}_tmp"
    )
    local_storage_cache_path = (
        f"/tmp/mtbls_unit_test_local_cache_{random.randint(1000000, 9999999)}_tmp"
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

        provider = MetabolightsSubmissionRepository(
            credentials_file_path=credentials_file_path,
            local_storage_root_path=local_storage_root_path,
            local_storage_cache_path=local_storage_cache_path,
        )
        mocker.patch(
            "metabolights_utils.provider.submission_repository.httpx.post",
            return_value=MockHttpResponse(
                status_code=200, text='{"filename": "a_str.txt", "maf": "m_str.tsv"}'
            ),
        )
        assay, maf, message = provider.create_assay(
            "MTBLS5397", "LC-MS", column_type="hilic", scan_polarity="positive"
        )
        assert not message
        assert assay == "a_str.txt"
        assert maf == "m_str.tsv"
        current_api_token = provider.get_api_token
        provider.get_api_token = lambda: (None, "error")
        assay, maf, message = provider.create_assay(
            "MTBLS5397", "LC-MS", column_type="hilic", scan_polarity="positive"
        )
        assert message == "error"
        assert not assay
        assert not maf
        provider.get_api_token = current_api_token
        mocker.patch(
            "metabolights_utils.provider.submission_repository.httpx.post",
            return_value=MockHttpResponse(
                status_code=200, text='{"filename": "a_str.txt"}'
            ),
        )

        assay, maf, message = provider.create_assay(
            None, "LC-MS", column_type="hilic", scan_polarity="positive"
        )
        assert "study_id or assay_technique is not defined" in message
        assert not assay
        assert not assay

        assay, maf, message = provider.create_assay(
            "MTBLS5397", "LC-MS", column_type="hilic", scan_polarity="positive"
        )
        assert "Invalid response" in message
        assert not assay
        assert not assay

        mocker.patch(
            "metabolights_utils.provider.submission_repository.httpx.post",
            return_value=MockHttpResponse(
                status_code=400, text='{"filename": "a_str.txt"}'
            ),
        )
        assay, maf, message = provider.create_assay(
            "MTBLS5397", "LC-MS", column_type="hilic", scan_polarity="positive"
        )
        assert message == 400
        assert not assay
        assert not assay

        mocker.patch(
            "metabolights_utils.provider.submission_repository.httpx.post",
            side_effect=TimeoutError("timeout error"),
        )
        assay, maf, message = provider.create_assay(
            "MTBLS5397", "LC-MS", column_type="hilic", scan_polarity="positive"
        )
        assert message == "timeout error"
        assert not assay
        assert not assay

    except Exception as ex:
        assert False, f"Error: {ex}"
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)
        if os.path.exists(local_storage_root_path):
            shutil.rmtree(local_storage_root_path)
        if os.path.exists(local_storage_cache_path):
            shutil.rmtree(local_storage_cache_path)


@pytest.fixture
def submission_repository():
    credentials_file_path = (
        f"/tmp/mtbls_unit_test_load_study_{random.randint(1000000, 9999999)}_tmp"
    )
    local_storage_root_path = (
        f"/tmp/mtbls_unit_test_load_study_{random.randint(1000000, 9999999)}_tmp"
    )
    local_storage_cache_path = f"/tmp/mtbls_unit_test_local_cache_load_study_{random.randint(1000000, 9999999)}_tmp"
    try:
        credentials = {
            "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
            "rest_api_credentials": {
                "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
            },
        }
        with open(credentials_file_path, "w") as f:
            json.dump(credentials, f)

        repository = MetabolightsSubmissionRepository(
            local_storage_root_path=local_storage_root_path,
            local_storage_cache_path=local_storage_cache_path,
            credentials_file_path=credentials_file_path,
        )
        yield repository, credentials
    except Exception as ex:
        assert False, f"Error: {ex}"
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)
        if os.path.exists(local_storage_root_path):
            shutil.rmtree(local_storage_root_path)
        if os.path.exists(local_storage_cache_path):
            shutil.rmtree(local_storage_cache_path)


def test_load_study_model_01(submission_repository):
    repository, credentials = submission_repository
    model, messages = repository.load_study_model(
        None,
        use_only_local_path=True,
        override_local_files=False,
        load_folder_metadata=False,
        folder_index_file_path=None,
    )
    assert not model
    assert messages and "Invalid study_id" in messages[0].short


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_load_study_model_02(submission_repository, study_id):
    repository, credentials = submission_repository
    model, messages = repository.load_study_model(
        study_id=study_id,
        local_path="tests/test-data",
        use_only_local_path=True,
        override_local_files=False,
        load_folder_metadata=False,
        folder_index_file_path=None,
    )
    assert model
    assert model.investigation.identifier == study_id
    assert messages and "Loaded from local isa metadata" in messages[0].short


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_load_study_model_03(submission_repository, study_id):
    repository, credentials = submission_repository
    model, messages = repository.load_study_model(
        study_id=study_id,
        use_only_local_path=True,
        override_local_files=False,
        load_folder_metadata=False,
        folder_index_file_path=None,
    )
    assert model
    assert model.folder_reader_messages


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_load_study_model_04(submission_repository, study_id):
    repository, credentials = submission_repository

    repository.download_submission_metadata_files = lambda **argv: LocalDirectory(
        success=True
    )
    model, messages = repository.load_study_model(
        study_id=study_id,
        local_path="tests/test-data",
        use_only_local_path=False,
        override_local_files=False,
        load_folder_metadata=False,
        folder_index_file_path=None,
    )
    assert model
    assert model.investigation.identifier == study_id


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_load_study_model_05(submission_repository, study_id):
    repository, credentials = submission_repository

    repository.download_submission_metadata_files = lambda **argv: LocalDirectory(
        success=False
    )
    model, messages = repository.load_study_model(
        study_id=study_id,
        local_path="tests/test-data",
        use_only_local_path=False,
        override_local_files=False,
        load_folder_metadata=False,
        folder_index_file_path=None,
    )
    assert not model
    assert messages and "Download metadata file failure" in messages[0].short


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_load_study_model_06(submission_repository, study_id):
    repository, credentials = submission_repository

    def raise_exception(**argv):
        raise ValueError("Request failed")

    repository.download_submission_metadata_files = raise_exception

    model, messages = repository.load_study_model(
        study_id=study_id,
        local_path="tests/test-data",
        use_only_local_path=False,
        override_local_files=False,
        load_folder_metadata=False,
        folder_index_file_path=None,
    )
    assert not model
    assert messages and "Request failed" in messages[0].detail


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_upload_metadata_01(submission_repository, study_id):
    """
    Test if there is no file
    """
    repository, credentials = submission_repository

    def list_response(**argv):
        # response = StudyResponse()
        # response.study.append(ResponseFileDescriptor(file="i_Investigation.txt"))
        return None, None

    repository.list_isa_metadata_files = list_response

    success, message = repository.upload_metadata_files(
        study_id=study_id,
        override_remote_files=False,
    )
    assert not success
    assert "Errors while listing metadata" in message


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_upload_metadata_02(submission_repository, study_id):
    """
    Test if there is no file
    """
    repository, credentials = submission_repository

    def list_response(**argv):
        response = StudyResponse()
        response.study.append(
            ResponseFileDescriptor(
                file="i_Investigation.txt", created_at="2024-05-01 15:21:01"
            )
        )
        return response, None

    repository.list_isa_metadata_files = list_response

    success, message = repository.upload_metadata_files(
        study_id=study_id,
        local_path="tests/test-data",
        override_remote_files=False,
    )
    assert not success
    assert "Remote folder does not defined" in message


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_upload_metadata_03(submission_repository, study_id):
    """
    Test if there is no file
    """
    repository, credentials = submission_repository

    def list_response(**argv):
        response = StudyResponse()
        response.upload_path = f"/pub/{study_id}"
        response.study.append(
            ResponseFileDescriptor(
                file="i_Investigation.txt", created_at="2024-05-01 15:21:01"
            )
        )
        return response, None

    repository.list_isa_metadata_files = list_response

    success, message = repository.upload_metadata_files(
        study_id=study_id,
        local_path="tests/test-data2",
        override_remote_files=False,
    )
    assert not success
    assert "Study path does not exist" in message


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_upload_metadata_04(mocker: MockerFixture, submission_repository, study_id):
    """
    Test if there is no file
    """

    mock_ftp = MagicMock()
    mocker.patch(
        "metabolights_utils.provider.submission_repository.DefaultFtpClient",
        return_value=mock_ftp,
    )

    mock_ftp.upload_files.side_effect = ValueError("Permission denied")

    repository, credentials = submission_repository

    def list_response(**argv):
        response = StudyResponse()
        response.upload_path = f"/pub/{study_id}"
        response.study.append(
            ResponseFileDescriptor(
                file="i_Investigation.txt", created_at="2024-05-01 15:21:01"
            )
        )
        return response, None

    repository.list_isa_metadata_files = list_response

    success, message = repository.upload_metadata_files(
        study_id=study_id,
        local_path="tests/test-data",
        override_remote_files=False,
    )
    assert not success
    assert "Permission denied" in message


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_upload_metadata_05(mocker: MockerFixture, submission_repository, study_id):
    """
    Test successfull upload
    """

    mock_ftp = MagicMock()
    mocker.patch(
        "metabolights_utils.provider.submission_repository.DefaultFtpClient",
        return_value=mock_ftp,
    )

    mock_ftp.upload_files.return_value = "Ok"

    repository, credentials = submission_repository

    def list_response(**argv):
        response = StudyResponse()
        response.upload_path = f"/pub/{study_id}"
        response.study.append(
            ResponseFileDescriptor(
                file="i_Investigation.txt", created_at="2024-05-01 15:21:01"
            )
        )
        return response, None

    repository.list_isa_metadata_files = list_response

    success, message = repository.upload_metadata_files(
        study_id=study_id,
        local_path="tests/test-data",
        override_remote_files=False,
    )
    assert success
    assert not message


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_validate_study_01(mocker: MockerFixture, submission_repository, study_id):
    """
    Test validation without error
    """

    # mock_ftp = MagicMock()
    mocker.patch(
        "metabolights_utils.provider.submission_repository.time.sleep",
        return_value=None,
    )

    class HttpxResponse(BaseModel):
        text: str = ""
        status_code: int = -1

    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.post",
        return_value=HttpxResponse(
            status_code=201,
            text=open(
                "tests/test-data/rest-api-test-data/validation_started_response.json"
            ).read(),
        ),
    )
    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.get",
        side_effect=[
            HttpxResponse(
                status_code=200,
                text=open(
                    "tests/test-data/rest-api-test-data/validation_success_response.json"
                ).read(),
            ),
            HttpxResponse(
                status_code=200,
                text=open(
                    "tests/test-data/rest-api-test-data/validation_report.json"
                ).read(),
            ),
        ],
    )
    # mock_ftp.upload_files.return_value = "Ok"

    repository, credentials = submission_repository

    # repository.list_isa_metadata_files = list_response
    validation_file_path = (
        f"/tmp/mtbls_unit_test_validation_{random.randint(1000000, 9999999)}_tmp.json"
    )
    try:
        success, message = repository.validate_study(
            study_id=study_id,
            validation_file_path=validation_file_path,
        )
        assert success
    finally:
        if os.path.exists(validation_file_path):
            os.remove(validation_file_path)
