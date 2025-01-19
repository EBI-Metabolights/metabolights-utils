import json
import os
import shutil
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from metabolights_utils.models.metabolights.model import MetabolightsStudyModel
from metabolights_utils.provider import definitions
from metabolights_utils.provider.ftp.folder_metadata_collector import FolderIndex
from metabolights_utils.provider.ftp.model import FtpFiles, LocalDirectory
from metabolights_utils.provider.ftp_repository import MetabolightsFtpRepository
from metabolights_utils.provider.local_folder_metadata_collector import (
    LocalFolderMetadataCollector,
)
from metabolights_utils.provider.utils import (
    is_metadata_file,
    is_metadata_filename_pattern,
)

valid_metadata_files = [
    "tests/test-data/MTBLS60/a_MTBLS60_dippA_UPLC_MS.txt",
    "tests/test-data/MTBLS60/m_MTBLS60_dippA_UPLC_MS_v2_maf.tsv",
    "tests/test-data/MTBLS66/s_MTBLS66.txt",
    "tests/test-data/MTBLS66/i_Investigation.txt",
]
invalid_metadata_files = [
    "tests/test-data/MTBLS60/a_MTBLS60_dippA_UPLC   _MSx.txt",
    "tests/test-data/MTBLS60/m_MTBLS60_dippA_UPLC_MS_v2_mafx.tsv",
    "tests/test-data/MTBLS66/s_MTBLS66x.txt",
    "tests/test-data/MTBLS66/i_Investigation.txt",
]


@pytest.mark.parametrize("file_path", valid_metadata_files)
def test_is_metadata_file_01(file_path: str):
    """Return true if it is valid study file path

    Args:
        filepath (str): valid study file paths
    """
    actual = is_metadata_file(file_path)
    assert actual


@pytest.mark.parametrize("file_path", invalid_metadata_files)
def test_is_metadata_file_02(mocker: MockerFixture, file_path: str):
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("os.path.isfile", return_value=False)

    actual = is_metadata_file(file_path)
    assert not actual


@pytest.mark.parametrize("file_path", invalid_metadata_files)
def test_is_metadata_file_03(mocker: MockerFixture, file_path: str):
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.path.isfile", return_value=False)

    actual = is_metadata_file(file_path)
    assert not actual


valid_filenames = [os.path.basename(x) for x in valid_metadata_files]


@pytest.mark.parametrize("file_path", valid_filenames)
def test_is_metadata_filename_pattern_01(file_path: str):
    actual = is_metadata_filename_pattern(file_path)
    assert actual


invalid_filename_inputs = [
    None,
    "",
    "a_Investigation.tsv",
    "i_.txt",
    "test.txt",
    "m_x.txt",
]


@pytest.mark.parametrize("file_path", invalid_filename_inputs)
def test_is_metadata_filename_pattern_02(file_path: str):
    actual = is_metadata_filename_pattern(file_path)
    assert not actual


@pytest.mark.parametrize("study_id", [None, "", "\t", " "])
def test_load_study_01(mocker: MockerFixture, study_id: str):
    client = MetabolightsFtpRepository()
    mock_ftp = MagicMock()

    mocker.patch("ftplib.FTP", return_value=mock_ftp)

    # mocker.patch.object(ftplib.FTP, "retrlines", return_value="200 Ok")
    model, messages = client.load_study_model(
        study_id,
        use_only_local_path=True,
    )
    assert not model
    assert messages


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_load_study__local_01(mocker: MockerFixture, study_id: str):
    client = MetabolightsFtpRepository()
    expected = "test.txt"
    mock_provider = MagicMock()
    mock_provider.load_study = lambda x, **argv: MetabolightsStudyModel(
        investigation_file_path=expected
    )
    mocker.patch(
        "metabolights_utils.provider.ftp_repository.MetabolightsStudyProvider",
        return_value=mock_provider,
    )

    model, messages = client.load_study_model(
        study_id, use_only_local_path=True, use_study_model_cache=False
    )
    assert model.investigation_file_path == expected


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_load_study__local_02(mocker: MockerFixture, study_id: str):
    client = MetabolightsFtpRepository()
    expected = "test.txt"
    mock_provider = MagicMock()
    mock_provider.load_study = lambda x, **argv: MetabolightsStudyModel(
        investigation_file_path=expected
    )
    mocker.patch(
        "metabolights_utils.provider.ftp_repository.MetabolightsStudyProvider",
        return_value=mock_provider,
    )

    client.download_study_metadata_files = lambda **argv: LocalDirectory(success=True)
    model, messages = client.load_study_model(
        study_id, use_only_local_path=False, use_study_model_cache=False
    )
    assert model.investigation_file_path == expected


def list_file(command: str, callback):
    data = """\
drwxr-sr-x   2 45854    200           512 May  4  2000 MTBLS1
drwxr-sr-x   2 45854    200           512 May  4  2000 MTBLS22
drwxr-sr-x   2 45854    200           512 May  4  2000 a_sschwarzer2.tsv
-rw-r--r--   1 45854    200          4605 Jan 19  1970 a_older.txt
-rw-r--r--   1 45854    200          4605 Jan 19  1970 i_older.txt
-rw-r--r--   1 45854    200          4605 Jan 19  1970 s_older.txt
-rw-r--r--   1 45854    200          4605 Jan 19  1970 m_older.tsv
-rw-r--r--   1 45854    200          4605 Jan 19  1970 older.tsv
-rw-r--r--   1 45854    200          4605 Jan 19  2020 newer
lrwxrwxrwx   1 45854    200            21 Jan 19  2002 link -> sschwarzer/index.html
"""
    data = data.split("\n")
    for i in range(10):
        callback(data[i])
    return "200 Ok"


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_load_study_02(mocker: MockerFixture, study_id: str):
    client = MetabolightsFtpRepository()
    mock_ftp = MagicMock()

    mocker.patch("ftplib.FTP", return_value=mock_ftp)
    local_path = "test-temp/ftp_client/test02"
    model = None
    try:
        os.makedirs(local_path, exist_ok=True)
        target_path = os.path.join(local_path, study_id)
        shutil.rmtree(target_path, ignore_errors=True)
        shutil.copytree(f"tests/test-data/{study_id}", target_path)
        model, messages = client.load_study_model(
            study_id,
            use_only_local_path=True,
            local_path=local_path,
            folder_index_file_path=None,
        )
    except Exception as ex:
        raise ex
    finally:
        shutil.rmtree(local_path, ignore_errors=True)
    assert model


def test_list_metadata_files_01(mocker: MockerFixture):
    client = MetabolightsFtpRepository()

    mock_ftp = MagicMock()

    mocker.patch("ftplib.FTP", return_value=mock_ftp)

    def mock_connect():
        client.ftp_client.ftp = mock_ftp

    client.ftp_client.connect = mock_connect
    mock_ftp.retrlines = list_file

    result = client.list_isa_metadata_files("MTBLS1")
    assert len(result.files) == 4
    client = MetabolightsFtpRepository(local_storage_root_path="metabolights_data")

    assert client


class MockFtpWriter:
    def __init__(self, source_path: str, remote_root_directory: str) -> None:
        self.remote_root_directory = remote_root_directory
        self.source_path = source_path
        self.current_path = self.source_path

    def retrbinary(self, command, file_writer):
        command_terms = command.split()
        if len(command_terms) > 1:
            file_name = command.replace(command_terms[0], "").strip()
        file_path = None
        if file_name:
            file_path = os.path.join(self.current_path, file_name)

        if file_path and os.path.exists(file_path):
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    file_writer(bytes(line, encoding="utf-8"))

    def retrlines(self, command: str, callback):
        command_terms = command.split()
        search_file = None

        if len(command_terms) > 1:
            search_file = command.replace(command_terms[0], "").strip()
        file_mode = "-rwxr-sr-x"
        directory_mode = "drwxr-sr-x"
        # link_mode = "lrwxr-sr-x"
        current_file_path = self.current_path
        if search_file:
            target_path = os.path.join(self.current_path, search_file)
            if os.path.exists(target_path):
                if os.path.isdir(target_path):
                    current_file_path = target_path
                elif os.path.isfile(target_path):
                    line = f"{file_mode}   2 45854    200           512 May  4  2000 {search_file}"
                    callback(line)
                    return "200 Ok"

        if not os.path.exists(current_file_path):
            return "400 Not a valid directory"

        files = os.listdir(current_file_path)
        for file in files:
            mode = file_mode
            file_path = os.path.join(current_file_path, file)
            if os.path.isdir(file_path):
                mode = directory_mode
            elif os.path.isfile(file_path):
                mode = file_mode
            line = f"{mode}   2 45854    200           512 May  4  2000 {file}"
            callback(line)

        return "200 Ok"

    def cwd(self, current_path: str):
        relative_path = current_path.replace(f"{self.remote_root_directory}/", "", 1)
        self.current_path = os.path.join(self.source_path, relative_path)


def test_download_study_data_files_01(mocker: MockerFixture):
    study_id = "MTBLS5195"
    client = MetabolightsFtpRepository()

    mock_ftp = MagicMock()
    mock_writer = MockFtpWriter(
        source_path="tests/test-data",
        remote_root_directory=definitions.default_remote_repository_root_directory,
    )
    mock_ftp.retrlines = mock_writer.retrlines
    mock_ftp.retrbinary = mock_writer.retrbinary
    mock_ftp.cwd = mock_writer.cwd

    mocker.patch("ftplib.FTP", return_value=mock_ftp)
    local_path = "test-temp/ftp_client/download_data_files_01"
    try:
        shutil.rmtree(local_path, ignore_errors=True)
        os.makedirs(local_path, exist_ok=True)

        def mock_connect():
            client.ftp_client.ftp = mock_ftp

        client.ftp_client.connect = mock_connect

        result = client.download_study_data_files(
            study_id, local_path=local_path, override_local_files=True
        )
        assert result.actions
    except Exception as ex:
        raise AssertionError("Error while testing download_study_data_files") from ex
    finally:
        shutil.rmtree(local_path, ignore_errors=True)


def test_download_study_metadata_files_01(mocker: MockerFixture):
    study_id = "MTBLS5195"
    client = MetabolightsFtpRepository()

    mock_ftp = MagicMock()
    mock_writer = MockFtpWriter(
        source_path="tests/test-data",
        remote_root_directory=definitions.default_remote_repository_root_directory,
    )
    mock_ftp.retrlines = mock_writer.retrlines
    mock_ftp.retrbinary = mock_writer.retrbinary
    mock_ftp.cwd = mock_writer.cwd

    mocker.patch("ftplib.FTP", return_value=mock_ftp)
    local_path = "test-temp/ftp_client/download_metadata_files_01"
    try:
        shutil.rmtree(local_path, ignore_errors=True)
        os.makedirs(local_path, exist_ok=True)

        def mock_connect():
            client.ftp_client.ftp = mock_ftp

        client.ftp_client.connect = mock_connect

        result = client.download_study_metadata_files(
            study_id, local_path=local_path, override_local_files=True
        )
        assert result.local_files
    except Exception as ex:
        raise AssertionError(
            "Error while testing download_study_metadata_files_01"
        ) from ex
    finally:
        shutil.rmtree(local_path, ignore_errors=True)


def test_download_study_metadata_files_02(mocker: MockerFixture):
    study_id = "MTBLS5195"
    client = MetabolightsFtpRepository()

    mock_ftp = MagicMock()
    mock_writer = MockFtpWriter(
        source_path="tests/test-data",
        remote_root_directory=definitions.default_remote_repository_root_directory,
    )
    mock_ftp.retrlines = mock_writer.retrlines
    mock_ftp.retrbinary = mock_writer.retrbinary
    mock_ftp.cwd = mock_writer.cwd

    mocker.patch("ftplib.FTP", return_value=mock_ftp)
    local_path = "test-temp/ftp_client/download_metadata_files_01"
    try:
        shutil.rmtree(local_path, ignore_errors=True)
        os.makedirs(local_path, exist_ok=True)

        def mock_connect():
            client.ftp_client.ftp = mock_ftp

        client.ftp_client.connect = mock_connect
        result = client.download_study_metadata_files(
            None, local_path=None, override_local_files=True
        )
        assert result.code == 400
        assert not result.root_path

        client.list_isa_metadata_files = lambda x: FtpFiles(
            success=False, code=400, message="test"
        )
        result = client.download_study_metadata_files(
            study_id, local_path=local_path, override_local_files=True
        )
        assert not result.success
        assert result.message == "test"
    except Exception as ex:
        raise AssertionError(
            "Error while testing test_download_study_metadata_files_02"
        ) from ex
    finally:
        shutil.rmtree(local_path, ignore_errors=True)


def test_list_studies_01(mocker: MockerFixture):
    client = MetabolightsFtpRepository()

    mock_ftp = MagicMock()
    mock_writer = MockFtpWriter(
        source_path="tests/test-data",
        remote_root_directory=definitions.default_remote_repository_root_directory,
    )
    mock_ftp.retrlines = mock_writer.retrlines
    mock_ftp.retrbinary = mock_writer.retrbinary
    mock_ftp.cwd = mock_writer.cwd

    mocker.patch("ftplib.FTP", return_value=mock_ftp)
    try:

        def mock_connect():
            client.ftp_client.ftp = mock_ftp

        client.ftp_client.connect = mock_connect

        result, messages = client.list_studies()
        assert "MTBLS1" in result
        assert not messages
    except Exception as ex:
        raise AssertionError("Error while testing list_studies_01") from ex


def test_list_study_folder_directory_01(mocker: MockerFixture):
    client = MetabolightsFtpRepository()

    mock_ftp = MagicMock()
    mock_writer = MockFtpWriter(
        source_path="tests/test-data",
        remote_root_directory=definitions.default_remote_repository_root_directory,
    )
    mock_ftp.retrlines = mock_writer.retrlines
    mock_ftp.retrbinary = mock_writer.retrbinary
    mock_ftp.cwd = mock_writer.cwd

    mocker.patch("ftplib.FTP", return_value=mock_ftp)
    try:

        def mock_connect():
            client.ftp_client.ftp = mock_ftp

        client.ftp_client.connect = mock_connect

        result = client.list_study_directory("MTBLS5195")
        assert result.files
        assert result.folders
        result = client.list_study_directory("MTBLS5195", "FILES")
        assert result.files
        assert not result.folders
    except Exception as ex:
        raise AssertionError(
            "Error while testing test_list_study_folder_directory_01"
        ) from ex


def test_get_study_folder_content_01(mocker: MockerFixture):
    study_id = "MTBLS5195"
    client = MetabolightsFtpRepository()

    mock_ftp = MagicMock()
    mock_writer = MockFtpWriter(
        source_path="tests/test-data",
        remote_root_directory=definitions.default_remote_repository_root_directory,
    )
    mock_ftp.retrlines = mock_writer.retrlines
    mock_ftp.retrbinary = mock_writer.retrbinary
    mock_ftp.cwd = mock_writer.cwd

    mocker.patch("ftplib.FTP", return_value=mock_ftp)
    local_path = "test-temp/ftp_client/test_get_study_folder_content_01"
    try:
        shutil.rmtree(local_path, ignore_errors=True)
        os.makedirs(local_path, exist_ok=True)

        def mock_connect():
            client.ftp_client.ftp = mock_ftp

        client.ftp_client.connect = mock_connect
        folder_index_file_path = os.path.join(local_path, "mtbls_index.json")
        result, message = client.get_study_folder_content(
            None,
            folder_index_file_path=folder_index_file_path,
            rebuild_folder_index_file=False,
        )
        assert not result

        result, message = client.get_study_folder_content(
            study_id,
            folder_index_file_path=folder_index_file_path,
            rebuild_folder_index_file=False,
        )
        assert result
        assert result.files
        assert os.path.exists(folder_index_file_path)
        assert "FILES/test.raw" in result.files
        with open(folder_index_file_path, encoding="utf-8") as f:
            data = json.load(f)
            index = FolderIndex.model_validate(data)
            assert "FILES/test.raw" in index.content.files
    except Exception as ex:
        raise AssertionError(
            "Error while testing test_get_study_folder_content_01"
        ) from ex
    finally:
        shutil.rmtree(local_path, ignore_errors=True)


def test_get_study_folder_content_02(mocker: MockerFixture):
    study_path = "tests/test-data/MTBLS1"
    real_path = os.path.realpath(study_path)
    collector = LocalFolderMetadataCollector()
    metadata, messages = collector.get_folder_metadata(
        study_path=real_path,
        calculate_data_folder_size=True,
        calculate_metadata_size=True,
    )

    assert metadata
    assert metadata.files
    assert not messages
