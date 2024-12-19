import json

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from metabolights_utils.commands.public.public_search import public_search


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_public_search_01(mocker: MockerFixture, study_id: str):
    mocker.patch(
        "metabolights_utils.commands.public.public_search.rest_api_post",
        return_value=(
            {
                "content": {
                    "page": [{"studyid": f"{study_id}"}],
                    "total": 1,
                    "pageSize": 1,
                },
                "status": "success",
            },
            None,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(public_search, ["--id"])
    assert result.exit_code == 0


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_public_search_02(mocker: MockerFixture, study_id: str):
    mocker.patch(
        "metabolights_utils.commands.public.public_search.rest_api_post",
        return_value=(
            None,
            "Failed to search studies",
        ),
    )

    runner = CliRunner()
    result = runner.invoke(public_search, ["--id"])
    assert result.exit_code == 1
    assert "Failed to search studies" in result.output


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_public_search_03(mocker: MockerFixture, study_id: str):
    with open(
        "tests/test-data/rest-api-test-data/study_search.json", "r", encoding="utf-8"
    ) as f:
        data = f.read()
        response = json.loads(data)
    mocker.patch(
        "metabolights_utils.commands.public.public_search.rest_api_post",
        return_value=(response, None),
    )
    runner = CliRunner()
    result = runner.invoke(public_search, [f"{study_id}"])
    assert result.exit_code == 0
    assert (
        f"MetaboLights public study search results for query: {study_id}"
        in result.output
    )


def test_public_search_04(mocker: MockerFixture):
    with open(
        "tests/test-data/rest-api-test-data/diet_search.json", "r", encoding="utf-8"
    ) as f:
        data = f.read()
        response = json.loads(data)
    mocker.patch(
        "metabolights_utils.commands.public.public_search.rest_api_post",
        return_value=(response, None),
    )
    runner = CliRunner()
    result = runner.invoke(public_search, ["diet"])
    assert result.exit_code == 0
    assert "MetaboLights public study search results for query: diet" in result.output

    result = runner.invoke(public_search, ["diet", "--id"])
    assert result.exit_code == 0
    assert "MTBLS225" in result.output

    result = runner.invoke(public_search, ["diet", "--raw", "--limit=1"])
    assert result.exit_code == 0
    assert "MTBLS225" in result.output


def test_public_search_05(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.commands.public.public_search.rest_api_post",
        return_value=(
            {
                "content": {
                    "page": [{"studyid": "MTBLS1"}],
                    "total": 0,
                    "pageSize": 1,
                },
                "status": "success",
            },
            None,
        ),
    )
    runner = CliRunner()
    result = runner.invoke(public_search, ["dietdiet", "--id"])
    assert result.exit_code == 0
    assert "[]" in result.output

    result = runner.invoke(public_search, ["dietdiet"])
    assert result.exit_code == 0
    assert "No results found" in result.output


def test_public_search_06(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.commands.public.public_search.rest_api_post",
        return_value=(
            {
                "content": {
                    "page": [{"studyid": "MTBLS1"}],
                    "total": 0,
                    "pageSize": 1,
                },
                "status": "failed",
            },
            "",
        ),
    )
    runner = CliRunner()
    result = runner.invoke(public_search, ["diet", "--id"])
    assert result.exit_code == 1
    assert "Failure of MetaboLights public study" in result.output


def test_public_search_07(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.commands.public.public_search.rest_api_post",
        return_value=(
            {
                "content": {
                    "page": [{"studyid": "MTBLS1"}],
                    "total": 0,
                },
                "status": "success",
            },
            None,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(public_search, ["diet"])
    assert result.exit_code == 1
    assert "Invalid response." in result.output


def test_public_search_08(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.commands.public.public_search.rest_api_post",
        return_value=(
            {
                "content": {
                    "page": [{"studyid": "MTBLS1"}],
                    "total": 0,
                },
                "status": "success",
            },
            None,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(public_search, ["diet", "--body=diet"])
    assert result.exit_code == 1
    # assert "Invalid response." in result.output


def test_public_search_09(mocker: MockerFixture):
    with open(
        "tests/test-data/rest-api-test-data/diet_aggregation_search.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = f.read()
        response = json.loads(data)
    mocker.patch(
        "metabolights_utils.commands.public.public_search.rest_api_post",
        return_value=(response, None),
    )

    runner = CliRunner()
    result = runner.invoke(
        public_search,
        [
            "--raw",
            "--body",
            '{"aggregations": [{ "aggregationName": "assay_techniques", "fieldName": "assayTechniques.name", "maxItemCount": 50, "minItemCount": 1}]}',
            "diet",
        ],
    )
    assert result.exit_code == 0
    assert "aggregations" in result.output
