import os
import pathlib
import uuid

from metabolights.isatab import Reader, Writer
from metabolights.isatab.reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights.isatab.writer import InvestigationFileWriter


def test_investigation_file_success_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)
    assert len(result.investigation.studies) == 1

    tmp_file_name = uuid.uuid4().hex
    tmp_path = pathlib.Path(f"/tmp/test_{tmp_file_name}.txt")
    writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
    writer.write(result.investigation, file_buffer_or_path=tmp_path)

    with open(tmp_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) > 0
    os.remove(tmp_path)
