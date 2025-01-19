import os
import shutil
import uuid
from pathlib import Path

import pytest

from metabolights_utils.utils.audit_utils import MetabolightsAuditUtils


@pytest.fixture(scope="function")
def tmp_path():
    tmp_path = None
    try:
        tmp_path = Path(f"test-temp/test_{uuid.uuid4().hex}")
        yield str(tmp_path)
    finally:
        if tmp_path and tmp_path.exists():
            shutil.rmtree(str(tmp_path))


def test_create_audit_folder_01(tmp_path: str):
    audit_path = MetabolightsAuditUtils.create_audit_folder(
        src_root_path="tests/test-data/MTBLS1", target_root_path=tmp_path
    )
    assert audit_path
    assert Path(audit_path).exists()
    audit_files = os.listdir(audit_path)
    source_files = os.listdir("tests/test-data/MTBLS1")
    files = [x for x in source_files if x.endswith(".txt") or x.endswith(".tsv")]
    assert len(audit_files) == len(files)


def test_create_audit_folder_non_exist_target_01(tmp_path: str):
    audit_path = MetabolightsAuditUtils.create_audit_folder(
        src_root_path="tests/test-data/MTBLS1x", target_root_path=tmp_path
    )
    assert not audit_path


def test_copy_isa_metadata_files_01(tmp_path: str):
    target_path = MetabolightsAuditUtils.copy_isa_metadata_files(
        src_folder_path="tests/test-data/MTBLS1", target_folder_path=tmp_path
    )
    assert target_path == tmp_path
    assert len(os.listdir(tmp_path)) > 0


def test_copy_isa_metadata_files_02(tmp_path: str):
    target_path = MetabolightsAuditUtils.copy_isa_metadata_files(
        src_folder_path="tests/test-data/MTBLS1x", target_folder_path=tmp_path
    )
    assert not target_path
    assert not Path(tmp_path).exists()
