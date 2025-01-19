import os
import random
from typing import Any, Dict, Generator, Tuple
from unittest.mock import MagicMock

import pytest

from metabolights_utils.provider.ftp.folder_metadata_collector import (
    FtpFolderMetadataCollector,
)
from metabolights_utils.provider.ftp.model import FtpFileDescriptor, FtpFolderContent
from metabolights_utils.provider.submission_repository import (
    MetabolightsSubmissionRepository,
)

valid_study_ids = [
    "MTBLS1",
]


@pytest.fixture
def folder_index_file_path() -> Generator[
    Tuple[MetabolightsSubmissionRepository, Dict[str, Any]], None, None
]:
    folder_index_file_path = (
        f"test-temp/mtbls_folder_index_file_path_{random.randint(1000000, 9999999)}_tmp"
    )
    try:
        os.makedirs(os.path.dirname(folder_index_file_path), exist_ok=True)
        return folder_index_file_path
    except Exception as ex:
        raise AssertionError(f"Error: {ex}")
    finally:
        if os.path.exists(folder_index_file_path):
            os.remove(folder_index_file_path)


@pytest.mark.parametrize("study_id", valid_study_ids)
def test_get_folder_metadata_01(folder_index_file_path: str, study_id: str):
    mock_client = MagicMock()
    mock_client.remote_repository_root_directory.return_value = "test-temp/path"
    folder_content = FtpFolderContent()
    folder_content.descriptors.append(
        FtpFileDescriptor(base_name="i_Investigation.txt", size_in_bytes=10, mode="755")
    )
    folder_content.descriptors.append(
        FtpFileDescriptor(base_name=f"s_{study_id}.txt", size_in_bytes=10, mode="755")
    )
    folder_content.descriptors.append(
        FtpFileDescriptor(base_name=f"s_{study_id}.txt", size_in_bytes=10, mode="755")
    )

    mock_client.list_directory.side_effect = [folder_content, FtpFolderContent()]

    mock_client.remote_repository_root_directory = "test-repo"
    collector = FtpFolderMetadataCollector(
        client=mock_client,
        study_id=study_id,
        folder_index_file_path=folder_index_file_path,
    )

    metadata, messages = collector.get_folder_metadata(None, False, False)

    assert len(metadata.files) == 2

    # reuse same file
    metadata, messages = collector.get_folder_metadata(None, False, False)
    assert len(metadata.files) == 2

    # reuse same file
    with open(folder_index_file_path, "w", encoding="utf-8") as f:
        f.write("invalid data")
    metadata, messages = collector.get_folder_metadata(None, False, False)
    assert len(metadata.files) == 0
    assert len(messages) > 0

    # reuse same file
    with open(folder_index_file_path, "w", encoding="utf-8") as f:
        f.write("{}")
    metadata, messages = collector.get_folder_metadata(None, False, False)
    assert len(metadata.files) == 0
    assert len(messages) > 0
