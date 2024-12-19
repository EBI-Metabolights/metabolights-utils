import os
from unittest import mock
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from metabolights_utils.commands.public.public_list import public_list
from metabolights_utils.models.common import ErrorMessage


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_public_list_01(mocker: MockerFixture, study_id: str):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_list.MetabolightsFtpRepository",
        return_value=mock_repository,
    )
    mock_repository.list_studies.return_value = (
        [f"MTBLS{i}" for i in range(1, 6000)],
        [],
    )

    runner = CliRunner()
    result = runner.invoke(public_list)
    assert result.exit_code == 0
    assert "FTP Public study" in result.output

    mock_repository.list_studies.return_value = (
        [f"MTBLS{i}" for i in range(1, 10)],
        [],
    )
    result = runner.invoke(public_list)
    assert result.exit_code == 0
    assert "FTP Public study" in result.output


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_public_list_02(mocker: MockerFixture, study_id: str):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_list.MetabolightsFtpRepository",
        return_value=mock_repository,
    )

    mock_repository.list_studies.return_value = (
        [f"MTBLS{i}" for i in range(1, 10)],
        [ErrorMessage(short="error message 1")],
    )

    runner = CliRunner()
    result = runner.invoke(public_list)
    assert result.exit_code == 1
    assert "error message 1" in result.output


@mock.patch(
    "os.listdir", mock.MagicMock(return_value=[f"MTBLS{i}" for i in range(1, 3)])
)
def test_public_list_03(mocker: MockerFixture):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_list.MetabolightsFtpRepository",
        return_value=mock_repository,
    )

    mock_repository.list_studies.return_value = (
        [f"MTBLS{i}" for i in range(1, 10)],
        [],
    )

    runner = CliRunner()
    result = runner.invoke(public_list, ["-l"])
    assert result.exit_code == 0
    assert "Local public study" in result.output


@mock.patch(
    "os.listdir", mock.MagicMock(return_value=[f"MTBLS{i}" for i in range(1, 600)])
)
def test_public_list_04(mocker: MockerFixture):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_list.MetabolightsFtpRepository",
        return_value=mock_repository,
    )

    mock_repository.list_studies.return_value = (
        [f"MTBLS{i}" for i in range(1, 600)],
        [],
    )

    runner = CliRunner()
    result = runner.invoke(public_list, "-l")
    assert result.exit_code == 0
    assert "Local public study" in result.output


@mock.patch("os.listdir", mock.MagicMock(return_value=[]))
def test_public_list_05(mocker: MockerFixture):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_list.MetabolightsFtpRepository",
        return_value=mock_repository,
    )

    mock_repository.list_studies.return_value = (
        [f"MTBLS{i}" for i in range(1, 10)],
        [],
    )

    runner = CliRunner()
    result = runner.invoke(public_list, "-l")
    assert result.exit_code == 0
    assert "No public studies found on local storage" in result.output


def test_public_list_06():
    runner = CliRunner()
    local_path = os.path.realpath("tests/test-data")
    result = runner.invoke(
        public_list, ["-l", "MTBLS1", "FILES", "--local_path", local_path]
    )
    assert result.exit_code == 0
    assert "RAW_FILES" in result.output


def test_public_list_07():
    runner = CliRunner()
    local_path = os.path.realpath("tests/test-data")
    result = runner.invoke(public_list, ["-l", "MTBLS1", "--local_path", local_path])
    assert result.exit_code == 0
    assert "s_MTBLS1.txt" in result.output


def test_public_list_08():
    runner = CliRunner()
    local_path = os.path.realpath("tests/test-data")
    result = runner.invoke(public_list, ["-l", "--local_path", local_path])
    assert result.exit_code == 0
    assert "MTBLS1" in result.output


def test_public_list_09(mocker: MockerFixture):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_list.MetabolightsFtpRepository",
        return_value=mock_repository,
    )
    mock_response = MagicMock()
    mock_repository.list_study_directory.return_value = mock_response

    runner = CliRunner()
    mock_response.success = False
    result = runner.invoke(public_list, "MTBLS1")
    assert result.exit_code == 1
    assert "FTP response error" in result.output


def test_public_list_10(mocker: MockerFixture):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_list.MetabolightsFtpRepository",
        return_value=mock_repository,
    )
    mock_response = MagicMock()
    mock_repository.list_study_directory.return_value = mock_response

    runner = CliRunner()
    mock_response.success = True
    mock_response.files = ["s_MTBLS1.txt"]
    mock_response.folders = ["FILES/RAW_FILES"]

    result = runner.invoke(public_list, "MTBLS1")
    assert result.exit_code == 0
    assert "s_MTBLS1.txt" in result.output
    assert "FILES/RAW_FILES" in result.output
