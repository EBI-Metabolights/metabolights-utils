import os
import random
import shutil

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from metabolights_utils.commands.public.public_remove import public_remove


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_public_remove_01(mocker: MockerFixture, study_id: str):
    runner = CliRunner()

    mocker.patch(
        "metabolights_utils.commands.public.public_remove.os.path.exists",
        return_value=True,
    )
    mocker.patch(
        "metabolights_utils.commands.public.public_remove.shutil.rmtree",
        return_value=True,
    )
    result = runner.invoke(public_remove, [study_id])
    assert result.exit_code == 0
    assert "folders are deleted" in result.output


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_public_remove_02(mocker: MockerFixture, study_id: str):
    runner = CliRunner()

    mocker.patch(
        "metabolights_utils.commands.public.public_remove.os.path.exists",
        return_value=False,
    )
    mocker.patch(
        "metabolights_utils.commands.public.public_remove.shutil.rmtree",
        return_value=True,
    )
    result = runner.invoke(public_remove, [study_id])
    assert result.exit_code == 0
    assert "There is no folder for study" in result.output


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_public_remove_03(mocker: MockerFixture, study_id: str):
    mocker.patch(
        "metabolights_utils.commands.public.public_remove.os.path.exists",
        side_effect=FileNotFoundError,
    )
    mocker.patch(
        "metabolights_utils.commands.public.public_remove.shutil.rmtree",
        return_value=True,
    )
    runner = CliRunner()

    result = runner.invoke(public_remove, [study_id])
    assert result.exit_code == 1
    # assert mocked_exist.call_count == 1
    # assert mocked_rmtree.call_count == 0
    # assert mocked_rmtree.assert_not_called()

    assert f"Remove study {study_id} error:" in result.output


@pytest.mark.parametrize("study_id", ["MTBLS1X"])
def test_public_remove_04(study_id: str):
    runner = CliRunner()

    result = runner.invoke(public_remove, [study_id])
    assert result.exit_code == 0

    assert "There is no folder for study" in result.output


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_public_remove_05(study_id: str):
    runner = CliRunner()
    local_path = f"test-temp/{random.randint(1000000, 9999999)}"
    local_cache_path = f"test-temp/{random.randint(1000000, 9999999)}_tmp"
    try:
        study_path = os.path.join(local_path, study_id)
        study_cache_path = os.path.join(local_cache_path, study_id)
        os.makedirs(study_path, exist_ok=True)
        os.makedirs(study_cache_path, exist_ok=True)
        assert os.path.exists(study_path)
        assert os.path.exists(study_cache_path)

        result = runner.invoke(
            public_remove,
            [
                study_id,
                "--local_path",
                local_path,
                "--local_cache_path",
                local_cache_path,
            ],
        )
        assert result.exit_code == 0

        assert not os.path.exists(study_path)
        assert not os.path.exists(study_cache_path)
        assert f"Study {study_id} folders are deleted." in result.output
    except Exception as ex:
        raise AssertionError(f"Error: {ex}")
    finally:
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        if os.path.exists(local_cache_path):
            shutil.rmtree(local_cache_path)
