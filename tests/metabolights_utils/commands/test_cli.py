import pytest
from click.testing import CliRunner

from metabolights_utils.commands.cli import cli


def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0


model_cli_commands = [
    ["model", "explain"],
    ["model", "explain", "investigation.studies"],
    ["model", "explain", "assays.assay_technique.name"],
    ["model", "explain", "study_db_metadata.status"],
    ["model", "explain", "assays.table.data"],
    ["model", "explain", "assays.table.headers.column_index"],
    ["model", "explain", "parser_messages.type"],
    ["model", "explain", "assays.table.headers.column_structure"],
    ["model", "explain", "assays.assay_technique"],
    ["model", "explain", "investigation.studies.study_protocols"],
    ["model", "explain", "investigation.studies.study_protocols.comments"],
    ["model", "explain", "tags"],
]


@pytest.mark.parametrize("command_arguments", model_cli_commands)
def test_model_cli_01(command_arguments):
    runner = CliRunner()
    result = runner.invoke(cli, command_arguments)
    assert result.exit_code == 0


invalid_model_cli_commands = [
    ["model", "explain", "assays.table.headers.value"],
    ["model", "explain", "data"],
]


@pytest.mark.parametrize("command_arguments", invalid_model_cli_commands)
def test_model_cli_02(command_arguments):
    runner = CliRunner()
    result = runner.invoke(cli, command_arguments)
    assert result.exit_code == 1
