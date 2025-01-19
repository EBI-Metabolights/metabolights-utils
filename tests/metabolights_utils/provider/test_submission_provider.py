import datetime
import json
import os
import random
import shutil
from pathlib import Path
from typing import Any, Dict, Generator, Tuple
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel
from pytest_mock import MockerFixture

from metabolights_utils.commands.submission.model import (
    ResponseFileDescriptor,
    StudyResponse,
    SubmittedStudiesResponse,
)
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
        f"test-temp/mtbls_unit_test_login{random.randint(1000000, 9999999)}_tmp"
    )
    local_storage_root_path = (
        f"test-temp/mtbls_unit_test_local{random.randint(1000000, 9999999)}_tmp"
    )
    local_storage_cache_path = (
        f"test-temp/mtbls_unit_test_local_cache_{random.randint(1000000, 9999999)}_tmp"
    )
    try:
        test_data = {
            "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
            "rest_api_credentials": {
                "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
            },
        }
        with open(credentials_file_path, "w", encoding="utf-8") as f:
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
        raise AssertionError(f"Error: {ex}")
    finally:
        if os.path.exists(credentials_file_path):
            os.remove(credentials_file_path)
        if os.path.exists(local_storage_root_path):
            shutil.rmtree(local_storage_root_path)
        if os.path.exists(local_storage_cache_path):
            shutil.rmtree(local_storage_cache_path)


@pytest.fixture
def submission_repository() -> Generator[
    Tuple[MetabolightsSubmissionRepository, Dict[str, Any]], None, None
]:
    credentials_file_path = (
        f"test-temp/mtbls_unit_test_load_study_{random.randint(1000000, 9999999)}_tmp"
    )
    local_storage_root_path = (
        f"test-temp/mtbls_unit_test_load_study_{random.randint(1000000, 9999999)}_tmp"
    )
    local_storage_cache_path = f"test-temp/mtbls_unit_test_local_cache_load_study_{random.randint(1000000, 9999999)}_tmp"
    try:
        credentials = {
            "ftp_login": {"ftp-private.ebi.ac.uk": {"user_name": "x", "password": "y"}},
            "rest_api_credentials": {
                "https://www.ebi.ac.uk/metabolights/ws": {"api_token": "z"}
            },
        }
        with open(credentials_file_path, "w", encoding="utf-8") as f:
            json.dump(credentials, f)

        repository = MetabolightsSubmissionRepository(
            local_storage_root_path=local_storage_root_path,
            local_storage_cache_path=local_storage_cache_path,
            credentials_file_path=credentials_file_path,
        )
        yield repository, credentials
    except Exception as ex:
        raise AssertionError(f"Error: {ex}")
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
    assert "Uploaded Files:" in message


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_validate_study_01(mocker: MockerFixture, submission_repository, study_id):
    """
    Test validation without error
    """

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
            text=Path(
                "tests/test-data/rest-api-test-data/validation_task_started_response.json"
            )
            .open(encoding="utf-8")
            .read(),
        ),
    )
    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.get",
        side_effect=[
            HttpxResponse(
                status_code=200,
                text=Path(
                    "tests/test-data/rest-api-test-data/validation_task_success_response.json"
                )
                .open(
                    encoding="utf-8",
                )
                .read(),
            ),
            HttpxResponse(
                status_code=200,
                text=Path("tests/test-data/rest-api-test-data/validation_report.json")
                .open(encoding="utf-8")
                .read(),
            ),
        ],
    )

    repository, credentials = submission_repository

    validation_file_path = Path(
        f"test-temp/mtbls_unit_test_validation_{random.randint(1000000, 9999999)}_tmp.json"
    )
    try:
        success, message = repository.validate_study(
            study_id=study_id,
            validation_file_path=str(validation_file_path),
        )
        assert success
    finally:
        if validation_file_path.exists():
            validation_file_path.unlink(missing_ok=True)


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_private_ftp_sync_01(
    mocker: MockerFixture,
    submission_repository: Tuple[MetabolightsSubmissionRepository, Dict[str, Any]],
    study_id,
):
    """
    Test private ftp sync (without error)
    """

    mocker.patch(
        "metabolights_utils.provider.submission_repository.time.sleep",
        return_value=None,
    )

    class HttpxResponse(BaseModel):
        text: str = ""
        status_code: int = -1

    get_response = HttpxResponse(
        status_code=201,
        text=open(
            "tests/test-data/rest-api-test-data/ftp_sync_task_started_response.json",
            encoding="utf-8",
        ).read(),
    )
    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.post",
        return_value=get_response,
    )

    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.get",
        return_value=HttpxResponse(
            status_code=200,
            text=open(
                "tests/test-data/rest-api-test-data/ftp_sync_task_success_response.json",
                encoding="utf-8",
            ).read(),
        ),
    )
    repository, credentials = submission_repository

    success, message = repository.sync_private_ftp_metadata_files(study_id=study_id)
    assert success

    get_response.status_code = 400
    get_response.text = None

    success, message = repository.sync_private_ftp_metadata_files(study_id=study_id)
    assert not success


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_download_submission_metadata_files_01(
    mocker: MockerFixture, submission_repository, study_id
):
    """
    Test private ftp sync (without error)
    """

    mocker.patch(
        "metabolights_utils.provider.submission_repository.download_file_from_rest_api",
        return_value=True,
    )

    repository, credentials = submission_repository

    def list_isa_metadata_files(*arg, **argv):
        response = StudyResponse()
        response.study.append(
            ResponseFileDescriptor(
                file="i_Investigation.txt", created_at="2024-01-12 14:00:03"
            )
        )
        return response, None

    repository.list_isa_metadata_files = list_isa_metadata_files

    response = repository.download_submission_metadata_files(study_id=study_id)
    assert response
    assert response.success

    response = repository.download_submission_metadata_files(study_id="")
    assert response
    assert not response.success


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_download_submission_metadata_files_02(
    mocker: MockerFixture, submission_repository, study_id
):
    """
    Test private ftp sync (without error)
    """

    mocker.patch(
        "metabolights_utils.provider.submission_repository.download_file_from_rest_api",
        return_value=True,
    )

    repository, credentials = submission_repository

    def list_isa_metadata_files(*arg, **argv):
        response = StudyResponse()
        response.study.append(
            ResponseFileDescriptor(
                file="i_Investigation.txt", created_at="2022-01-12 14:00:03"
            )
        )
        return response, None

    study_path = Path(repository.local_storage_root_path) / Path(study_id)
    # os.makedirs(study_path, exist_ok=True)
    study_path.mkdir(parents=True, exist_ok=True)
    for file in list_isa_metadata_files()[0].study:
        file_path = study_path / Path(file.file)
        with file_path.open("w", encoding="utf-8") as fw:
            fw.write("test\n")
        modified = datetime.datetime.strptime(  # noqa: DTZ007
            file.created_at,
            "%Y-%m-%d %H:%M:%S",
        ).timestamp()

        os.utime(study_path, (modified, modified))

    repository.list_isa_metadata_files = list_isa_metadata_files

    response = repository.download_submission_metadata_files(study_id=study_id)
    assert response
    assert response.success


def test_list_studies_01(mocker: MockerFixture, submission_repository):
    """
    Test list studies
    """

    mocker.patch(
        "metabolights_utils.provider.submission_repository.time.sleep",
        return_value=None,
    )

    response = SubmittedStudiesResponse()

    class HttpxResponse(BaseModel):
        text: str = ""
        status_code: int = -1

    get_response = HttpxResponse(status_code=200, text=response.model_dump_json())

    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.get",
        return_value=get_response,
    )

    repository, credentials = submission_repository

    success, message = repository.list_studies()
    assert success

    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.get",
        return_value=HttpxResponse(status_code=400, text=response.model_dump_json()),
    )
    success, message = repository.list_studies()
    assert not success


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_list_study_directory_01(
    mocker: MockerFixture, submission_repository, study_id: str
):
    """
    Test list studies
    """

    mocker.patch(
        "metabolights_utils.provider.submission_repository.time.sleep",
        return_value=None,
    )

    mocker.patch(
        "metabolights_utils.provider.submission_repository.rest_api_get",
        return_value=(
            StudyResponse().model_dump(),
            "",
        ),
    )

    repository, credentials = submission_repository

    success, message = repository.list_study_directory(
        study_id=study_id, subdirectory="FILES"
    )
    assert success

    mocker.patch(
        "metabolights_utils.provider.submission_repository.rest_api_get",
        return_value=(
            None,
            "Error",
        ),
    )
    success, message = repository.list_study_directory(
        study_id=study_id, subdirectory="FILES"
    )
    assert not success
    assert message
