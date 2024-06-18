import os

import pytest


valid_study_ids = [
    "MTBLS1",
]


@pytest.mark.parametrize("study_path", valid_study_ids)
def test_get_metadata_01(study_path: str):
    real_path = os.path.realpath(study_path)
    # collector = FtpFolderMetadataCollector()
