import os

import pytest

from metabolights_utils.provider.local_folder_metadata_collector import (
    LocalFolderMetadataCollector,
)

valid_study_paths = [
    "tests/test-data/MTBLS1",
]


@pytest.mark.parametrize("study_path", valid_study_paths)
def test_get_metadata_01(study_path: str):
    real_path = os.path.realpath(study_path)
    collector = LocalFolderMetadataCollector()

    metadata, errors = collector.get_folder_metadata(study_path=real_path)
    assert metadata
    assert len(metadata.files) > 3
    assert len(metadata.folders) > 1

    assert not metadata.folder_size_in_str
    assert len(errors) == 0


@pytest.mark.parametrize("study_path", valid_study_paths)
def test_get_metadata_02(study_path: str):
    real_path = os.path.realpath(study_path)
    collector = LocalFolderMetadataCollector()

    metadata, errors = collector.get_folder_metadata(
        study_path=real_path,
        calculate_data_folder_size=True,
        calculate_metadata_size=False,
    )
    assert metadata
    assert metadata.folder_size_in_str
    assert len(errors) == 0

    metadata2, errors = collector.get_folder_metadata(
        study_path=real_path,
        calculate_data_folder_size=False,
        calculate_metadata_size=True,
    )

    assert metadata2
    assert metadata2.folder_size_in_str
    assert len(errors) == 0

    metadata3, errors = collector.get_folder_metadata(
        study_path=real_path,
        calculate_data_folder_size=True,
        calculate_metadata_size=True,
    )

    assert metadata3
    assert metadata3.folder_size_in_str
    assert len(errors) == 0

    assert metadata3.folder_size_in_bytes > metadata2.folder_size_in_bytes
    assert metadata2.folder_size_in_bytes > metadata.folder_size_in_bytes
