import os
import pathlib
import uuid

from pytest_mock import MockFixture

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.default.investigation_file import (
    DefaultInvestigationFileReader,
)
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights_utils.isatab.writer import InvestigationFileWriter


def test_investigation_file_success_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)
    assert len(result.investigation.studies) == 1

    tmp_file_name = uuid.uuid4().hex
    tmp_path = pathlib.Path(f"test-temp/test_{tmp_file_name}.txt")
    writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
    writer.write(result.investigation, file_buffer_or_path=tmp_path)

    with open(tmp_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) > 0
    os.remove(tmp_path)


def test_investigation_file_fail_01(mocker: MockFixture):
    class CustomError(UnicodeDecodeError):
        def __init__(self) -> None:
            super().__init__("utf-8", b"", -1, -1, "")

    def error(**argv):
        raise CustomError()

    file_path = "tests/test-data/MTBLS1/i_Investigation.txt"
    mocker.patch(
        "metabolights_utils.isatab.default.investigation_file.get_investigation",
        side_effect=CustomError,
    )
    reader: DefaultInvestigationFileReader = DefaultInvestigationFileReader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)
    assert result.parser_report.messages
