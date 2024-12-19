from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from metabolights_utils.commands.public.public_download import public_download


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_public_download_01(mocker: MockerFixture, study_id: str):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_download.MetabolightsFtpRepository",
        return_value=mock_repository,
    )

    mock_local_directory = MagicMock()
    mock_local_directory.success = True
    mock_local_directory.actions = {f"s_{study_id}.txt": "DOWNLOAD"}
    mock_repository.download_study_metadata_files.return_value = mock_local_directory
    mock_repository.local_storage_root_path = "test-temp/test"

    runner = CliRunner()
    result = runner.invoke(public_download, [study_id])
    assert result.exit_code == 0
    assert "Downloaded files on" in result.output

    result = runner.invoke(
        public_download,
        [study_id, "FILES/test.txt"],
    )
    assert result.exit_code == 0
    assert "Downloaded files on" in result.output


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_public_download_02(mocker: MockerFixture, study_id: str):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_download.MetabolightsFtpRepository",
        return_value=mock_repository,
    )

    mock_local_directory = MagicMock()
    mock_repository.download_study_metadata_files.return_value = mock_local_directory
    mock_repository.local_storage_root_path = "test-temp/test"

    mock_local_directory.actions = {}
    runner = CliRunner()
    result = runner.invoke(public_download, [study_id])
    assert result.exit_code == 0
    assert "There is no ISA metadata file" in result.output

    mock_local_directory.actions = {}
    mock_local_directory.success = False
    mock_local_directory.message = "Failed to download"
    result = runner.invoke(public_download, [study_id])
    assert result.exit_code == 1
    assert "FTP response error:" in result.output
    assert "Failed to download" in result.output
