import shutil
import uuid
from pathlib import Path

import pytest

from metabolights_utils.utils.audit_utils import MetabolightsAuditUtils
from metabolights_utils.utils.hash_utils import (
    EMPTY_FILE_HASH,
    IsaMetadataFolderHash,
    MetabolightsHashUtils,
)


@pytest.fixture(scope="function")
def tmp_path():
    tmp_path = None
    try:
        tmp_path = Path(f"test-temp/test_{uuid.uuid4().hex}")
        yield str(tmp_path)
    finally:
        if tmp_path and tmp_path.exists():
            shutil.rmtree(str(tmp_path))


def test_get_sha256sum_01():
    hash_val = MetabolightsHashUtils.sha256sum("tests/test-data/MTBLS1x")
    assert hash_val
    assert hash_val == EMPTY_FILE_HASH
    hash_val = MetabolightsHashUtils.sha256sum("")
    assert hash_val
    assert hash_val == EMPTY_FILE_HASH


def test_get_sha256sum_02():
    expected = "fa2f11ad5b556c57d8b8c03a6e8efe3e3b0ee62a7c0a0b725e640d1ce090d47f"
    hash_val = MetabolightsHashUtils.sha256sum(
        "tests/test-data/MTBLS1/i_Investigation.txt", convert_to_linux_line_ending=True
    )
    assert hash_val == expected


def test_get_isa_metadata_folder_hash_01():
    expected = EMPTY_FILE_HASH
    hash_val: IsaMetadataFolderHash = (
        MetabolightsHashUtils.get_isa_metadata_folder_hash("")
    )
    assert hash_val.folder_sha256 == expected
    assert len(hash_val.files_sha256) == 0
    hash_val = MetabolightsHashUtils.get_isa_metadata_folder_hash(
        "tests/test-data/MTBLS1x"
    )
    assert hash_val.folder_sha256 == expected
    assert len(hash_val.files_sha256) == 0


def test_get_isa_metadata_folder_hash_02():
    hash_val: IsaMetadataFolderHash = (
        MetabolightsHashUtils.get_isa_metadata_folder_hash("tests/test-data/MTBLS1")
    )
    assert hash_val.folder_sha256 != EMPTY_FILE_HASH
    assert len(hash_val.files_sha256) > 0


def test_get_isa_metadata_folder_hash_03(tmp_path: str):
    """
    additional isa medata files cause different hash
    """

    source_path = "tests/test-data/MTBLS1"
    target_path = MetabolightsAuditUtils.copy_isa_metadata_files(
        src_folder_path=source_path, target_folder_path=tmp_path
    )
    assert target_path == tmp_path
    assert len(list(Path(tmp_path).iterdir())) > 0

    hash_val: IsaMetadataFolderHash = (
        MetabolightsHashUtils.get_isa_metadata_folder_hash(tmp_path)
    )
    inv_file_path = str(Path(tmp_path) / Path("i_Investigation.txt"))
    target_file_path = str(Path(tmp_path) / Path("i_Investigation_2.txt"))
    shutil.copy(inv_file_path, target_file_path)
    hash_val2: IsaMetadataFolderHash = (
        MetabolightsHashUtils.get_isa_metadata_folder_hash(tmp_path)
    )
    assert hash_val.folder_sha256 != hash_val2.folder_sha256


def test_get_isa_metadata_folder_hash_04(tmp_path: str):
    """
    renamed files cause different hash
    """

    source_path = "tests/test-data/MTBLS1"
    target_path = MetabolightsAuditUtils.copy_isa_metadata_files(
        src_folder_path=source_path, target_folder_path=tmp_path
    )
    assert target_path == tmp_path
    assert len(list(Path(tmp_path).iterdir())) > 0

    hash_val: IsaMetadataFolderHash = (
        MetabolightsHashUtils.get_isa_metadata_folder_hash(tmp_path)
    )
    inv_file_path = str(Path(tmp_path) / Path("i_Investigation.txt"))
    target_file_path = str(Path(tmp_path) / Path("i_Investigation_2.txt"))
    shutil.move(inv_file_path, target_file_path)
    hash_val2: IsaMetadataFolderHash = (
        MetabolightsHashUtils.get_isa_metadata_folder_hash(tmp_path)
    )
    assert hash_val.folder_sha256 != hash_val2.folder_sha256
