import os
from typing import List
from unittest.mock import MagicMock

import pytest

from metabolights_utils.commands.utils import (
    convert_html_to_plain_text,
    find_column_names,
    get_unique_values,
    print_study_model_summary,
    split_to_lines,
    sub_arrays,
)
from metabolights_utils.models.common import CriticalMessage, ErrorMessage, InfoMessage
from metabolights_utils.models.isa.common import IsaTable
from metabolights_utils.models.metabolights.model import (
    StudyDBMetadata,
    StudyFolderMetadata,
)
from metabolights_utils.provider.study_provider import MetabolightsStudyProvider

arrays = [
    ([], 2, 0),
    (None, 2, 0),
    (["a", "b", "c", "d", "e", "f", "g"], 2, 4),
    (["a", "b", "c", "d", "e", "f", "g"], 6, 2),
    (["a", "b", "c", "d", "e", "f", "g"], 7, 1),
    (["a", "b", "c", "d", "e", "f", "g"], 10, 1),
]


@pytest.mark.parametrize("arr,k,result", arrays)
def test_sub_arrays(arr, k, result):
    actual = sub_arrays(arr, k)
    assert len(actual) == result


def test_sub_arrays_01():
    arr = ["a", "b", "c", "d", "e", "f", "g"]
    with pytest.raises(ValueError):
        sub_arrays(arr, -1)


def test_find_column_names_01():
    result = find_column_names(isa_table=None, pattern=None)
    assert len(result) == 0
    isa_table = IsaTable()
    isa_table.columns = ["Sample Name"]
    result = find_column_names(isa_table=isa_table, pattern=None)
    assert result == isa_table.columns


def test_find_column_names_02():
    isa_table = IsaTable()
    isa_table.columns = [
        "Sample Name",
        "Parameter Value[Instrument].2",
        "Parameter Value[Data]",
        "Parameter Value[Data ]",
        "Parameter[]",
    ]
    pattern = r".*Parameter.+Value.*\[.+\].*"
    result = find_column_names(isa_table=isa_table, pattern=pattern)
    assert len(result) == 3
    assert "Parameter Value[Data]" in result
    assert "Parameter Value[Instrument].2" in result


def test_get_unique_values_01():
    result = get_unique_values(None)
    assert len(result) == 0

    result = get_unique_values(["a", "b", "c"])
    assert len(result) == 3

    result = get_unique_values(["a", "b", "c", "a"])
    assert len(result) == 3


def test_convert_html_to_plain_text_01():
    result = convert_html_to_plain_text(None)
    assert len(result) == 0

    result = convert_html_to_plain_text("<a>Result</a>")
    assert result == "Result"
    value = bytes("<a><p>test</a>", encoding="utf-8").decode("iso-8859-9")
    try:
        result = convert_html_to_plain_text(value)
        assert result == "test"
    except Exception as ex:
        raise AssertionError(f"Encoding error: {str(ex)}")


def test_split_to_lines_01():
    result = split_to_lines(None)
    assert len(result) == 0

    data = """\
100 years old is such a young age if you happen to be a bristlecone pine.
I really want to go to work, but I am too sick to drive.
The bullet pierced the window shattering it before missing Danny's head by mere millimeters.
Doris enjoyed tapping her nails on the table to annoy everyone.
"""
    result = split_to_lines(data)
    assert len(result) > 1

    result = split_to_lines(data, max_line_size=10000)
    assert len(result) == 1

    result = split_to_lines(data, max_line_size=100, sep="\n")
    assert len(result) == 4

    result = split_to_lines(data, max_line_size=70, sep=" ")
    assert len(result) == 5


class MockLogger:
    def __init__(self) -> None:
        self.messages: List[str] = []

    def print(self, message: str):
        self.messages.append(message)


def test_print_study_model_summary_01():
    mock_logger = MockLogger()
    print_study_model_summary(None, log=mock_logger.print)
    assert len(mock_logger.messages) == 0


@pytest.mark.parametrize(
    "study_id",
    [
        "MTBLS1",
        "MTBLS60",
        "MTBLS5195",
        "MTBLS4861",
        "MTBLS66",
        "MTBLS9999999",
    ],
)
def test_print_study_model_summary_02(study_id: str):
    db_collector = MagicMock()
    db_collector.get_study_metadata_from_db.return_value = (
        StudyDBMetadata(),
        [ErrorMessage(short="x"), CriticalMessage(short="y")],
    )
    connection = MagicMock()
    folder_collector = MagicMock()
    folder_collector.get_folder_metadata.return_value = (
        StudyFolderMetadata(),
        [ErrorMessage(short="x"), CriticalMessage(short="y"), InfoMessage(short="z")],
    )
    client = MetabolightsStudyProvider(
        db_metadata_collector=db_collector, folder_metadata_collector=folder_collector
    )
    study_relative_path = f"tests/test-data/{study_id}"
    study_path = os.path.realpath(study_relative_path)

    model = client.load_study(
        study_id,
        study_path=study_path,
        connection=connection,
        load_assay_files=True,
        load_folder_metadata=True,
        load_sample_file=True,
        load_maf_files=True,
    )
    mock_logger = MockLogger()
    print_study_model_summary(model, log=mock_logger.print)

    assert len(mock_logger.messages) > 1
    assert mock_logger.messages[0].startswith(study_id)
