import os
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from metabolights_utils.commands.public.public_describe import public_describe
from metabolights_utils.provider.study_provider import MetabolightsStudyProvider


@pytest.mark.parametrize("study_id", ["MTBLS1", "MTBLS60"])
def test_public_describe(mocker: MockerFixture, study_id: str):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_describe.MetabolightsFtpRepository",
        return_value=mock_repository,
    )
    client = MetabolightsStudyProvider()
    study_relative_path = f"tests/test-data/{study_id}"
    study_path = os.path.realpath(study_relative_path)

    model = client.load_study(
        study_id,
        study_path=study_path,
        load_assay_files=True,
        load_folder_metadata=True,
        load_sample_file=True,
        load_maf_files=True,
    )

    mock_repository.load_study_model.return_value = (model, [])
    runner = CliRunner()
    result = runner.invoke(public_describe, [study_id])
    assert result.exit_code == 0
    assert result.output.startswith("MetaboLights study model summary.")
    assert f"{study_id}:" in result.output
    assert "Descriptors:" in result.output
    assert "Protocols:" in result.output
    assert "Assays:" in result.output
    assert "Metabolite Assignment Files (MAF):" in result.output

    result = runner.invoke(public_describe, [study_id, "assays[*].*.table.columns[*]"])
    assert result.exit_code == 0
    assert "search result:" in result.output

    result = runner.invoke(
        public_describe, [study_id, "investigation.studies[0].title"]
    )
    assert result.exit_code == 0
    assert "search result:" in result.output

    result = runner.invoke(
        public_describe, [study_id, "investigation.studies[0].titleX"]
    )
    assert result.exit_code == 0
    assert "no match" in result.output


@pytest.mark.parametrize("study_id", ["MTBLS1"])
def test_public_describe_02(mocker: MockerFixture, study_id: str):
    mock_repository = MagicMock()
    mocker.patch(
        "metabolights_utils.commands.public.public_describe.MetabolightsFtpRepository",
        return_value=mock_repository,
    )
    mock_model = MagicMock()
    mock_model.model_dump.side_effect = ValueError

    mock_repository.load_study_model.return_value = (None, [])

    runner = CliRunner()

    result = runner.invoke(
        public_describe, [study_id, "investigation.studies[0].title"]
    )
    assert result.exit_code > 0
    assert "Failure:" in result.output

    mock_model = MagicMock()
    mock_model.model_dump.side_effect = ValueError
    mock_model.investigation.studies = [MagicMock()]
    mock_repository.load_study_model.return_value = (mock_model, [])

    result = runner.invoke(
        public_describe, [study_id, "investigation.studies[0].title"]
    )
    assert result.exit_code > 0
    assert "expression error:" in result.output
