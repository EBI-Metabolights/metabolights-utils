import os
import pathlib
import uuid
from typing import List

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.default.parser.investigation_parser import (
    parse_investigation_file_content,
    parse_investigation_from_fs,
)
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights_utils.isatab.writer import InvestigationFileWriter
from metabolights_utils.models.parser.common import ParserMessage
from metabolights_utils.utils.hash_utils import MetabolightsHashUtils as HashUtils


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
    tmp_path = pathlib.Path(f"test-temp/test_{tmp_file_name}.txt")
    try:
        writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
        writer.write(result.investigation, file_buffer_or_path=tmp_path)
        new_sha256 = HashUtils.sha256sum(tmp_path)

        assert new_sha256 == sha25_hash
        writer.write(
            result.investigation,
            file_buffer_or_path=tmp_path,
            values_in_quotation_mark=False,
        )
        new_sha256 = HashUtils.sha256sum(tmp_path)
        assert new_sha256 != sha25_hash
    except Exception as exc:
        raise exc
    finally:
        os.remove(tmp_path)


def parser_unidecode_error(f, file_path, messages):
    raise UnicodeDecodeError("utf-8", b"", -1, -1, "")


def parser_exception(f, file_path, messages):
    raise Exception()


def test_parse_investigation_from_fs_invalid_04():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_invalid.txt"
    )

    messages: List[ParserMessage] = []
    investigation, messages = parse_investigation_file_content(
        parser=parser_unidecode_error,
        file_path=file_path,
        messages=messages,
        fix_unicode_exceptions=False,
    )
    assert not investigation
    assert messages

    messages = []
    investigation, messages = parse_investigation_file_content(
        parser=parser_unidecode_error,
        file_path=file_path,
        messages=messages,
        fix_unicode_exceptions=True,
    )
    assert not investigation
    assert messages

    messages = []
    investigation, messages = parse_investigation_file_content(
        parser=parser_exception,
        file_path=file_path,
        messages=messages,
        fix_unicode_exceptions=True,
    )
    assert not investigation
    assert messages


def test_parse_investigation_from_fs_invalid_05():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_invalid_content.txt"
    )
    investigation, messages = parse_investigation_from_fs(file_path)
    assert investigation
    assert messages
