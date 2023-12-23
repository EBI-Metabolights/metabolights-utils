import os
import pathlib
import uuid

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.default.parser.investigation_parser import (
    parse_investigation_from_fs,
)
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights_utils.isatab.writer import InvestigationFileWriter
from metabolights_utils.tsv.utils import calculate_sha256


def test_parse_investigation_from_fs_valid_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    investigation, messages = parse_investigation_from_fs(file_path)
    assert investigation
    assert not messages


def test_parse_investigation_from_fs_invalid_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/xi_Investigation.txt")
    investigation, messages = parse_investigation_from_fs(file_path)
    assert not investigation
    assert messages


def test_parse_investigation_from_fs_invalid_02():
    file_path = pathlib.Path("tests/test-data/investigation-files/i_Investigation.txt")
    investigation, messages = parse_investigation_from_fs(file_path)
    assert not investigation
    assert messages


def test_parse_investigation_from_fs_invalid_03():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_incomplete.txt"
    )
    investigation, messages = parse_investigation_from_fs(file_path)
    assert investigation
    assert messages


def test_parse_investigation_from_fs_invalid_04():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_empty_lines.txt"
    )
    investigation, messages = parse_investigation_from_fs(file_path)
    assert investigation
    assert messages


def test_investigation_file_read_write_success_1():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)
    assert len(result.investigation.studies) == 1
    sha25_hash = result.sha256_hash

    tmp_file_name = uuid.uuid4().hex
    tmp_path = pathlib.Path(f"/tmp/test_{tmp_file_name}.txt")
    try:
        writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
        writer.write(result.investigation, file_buffer_or_path=tmp_path)
        new_sha256 = calculate_sha256(tmp_path)

        assert new_sha256 == sha25_hash
        writer.write(
            result.investigation,
            file_buffer_or_path=tmp_path,
            values_in_quatation_mark=False,
        )
        new_sha256 = calculate_sha256(tmp_path)
        assert new_sha256 != sha25_hash
    except Exception as exc:
        raise exc
    finally:
        os.remove(tmp_path)
