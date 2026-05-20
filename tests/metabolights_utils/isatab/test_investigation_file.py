import io
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
from metabolights_utils.models.isa.investigation_file import Funder


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


def test_investigation_file_success_02():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    bytes_data = io.BytesIO(file_path.read_bytes())
    result: InvestigationFileReaderResult = reader.read(bytes_data)
    assert len(result.investigation.studies) == 1


def test_investigation_file_success_03():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    bytes_io = io.BytesIO(file_path.read_bytes())
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=bytes_io)
    assert len(result.investigation.studies) == 1


def test_investigation_file_success_04():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    bytes_io = io.StringIO(file_path.read_text())
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=bytes_io)
    assert len(result.investigation.studies) == 1


def test_investigation_file_success_05():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_funders_01.txt"
    )
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)
    assert len(result.investigation.studies) == 1
    result.investigation.sync_fields_from_comments()
    funders = result.investigation.studies[0].funders
    assert len(funders) == 2
    funders.append(Funder(funder_name="Test1", funder_id="Test_ID", grant_ids=[]))
    result.investigation.sync_comments_from_fields()
    funder_comments = [
        x for x in result.investigation.studies[0].comments if x.name == "Funder"
    ]
    assert len(funder_comments) == 1
    assert len(funder_comments[0].value) == 1
    assert "Test1" in funder_comments[0].value[0]
    writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
    val = None
    with io.StringIO() as buffer:
        writer.write(result.investigation, file_buffer_or_path=buffer)
        assert buffer
        val = buffer.getvalue()
        assert val
        assert ";Test1" in val
    val_buffer = io.StringIO(val)
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=val_buffer)
    assert len(result.investigation.studies[0].funders) == 3


def test_investigation_file_success_06():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_funders_02.txt"
    )
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)
    assert len(result.investigation.studies) == 1
    result.investigation.sync_fields_from_comments()
    funders = result.investigation.studies[0].funders
    assert len(funders) == 5
    funders.append(Funder(funder_name="Test1", funder_id="Test_ID", grant_ids=[]))
    result.investigation.sync_comments_from_fields()
    funder_comments = [
        x for x in result.investigation.studies[0].comments if x.name == "Funder"
    ]
    assert len(funder_comments) == 1
    assert len(funder_comments[0].value) == 1
    assert "Test1" in funder_comments[0].value[0]
    writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
    val = None
    with io.StringIO() as buffer:
        writer.write(result.investigation, file_buffer_or_path=buffer)
        assert buffer
        val = buffer.getvalue()
        assert val
        assert ";Test1" in val
    val_buffer = io.StringIO(val)
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=val_buffer)
    assert len(result.investigation.studies[0].funders) == 6


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
