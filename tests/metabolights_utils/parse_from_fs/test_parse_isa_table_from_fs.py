import os
import pathlib
import shutil
import uuid
from typing import List

from metabolights_utils.isatab import Writer
from metabolights_utils.isatab.default.assay_file import DefaultAssayFileReader
from metabolights_utils.isatab.default.assignment_file import (
    DefaultAssignmentFileReader,
)
from metabolights_utils.isatab.default.parser.isa_table_parser import (
    parse_isa_file_content,
    parse_isa_table_sheet_from_fs,
)
from metabolights_utils.isatab.default.sample_file import DefaultSampleFileReader
from metabolights_utils.models.isa.enums import ColumnsStructure


def test_parse_isa_table_sheet_from_fs_valid_assay_01():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    patterns = DefaultAssayFileReader.patterns
    table, messages = parse_isa_table_sheet_from_fs(
        file_path, expected_patterns=patterns
    )

    assert table
    assert not messages


def test_parse_isa_table_sheet_from_fs_valid_sample_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/s_MTBLS1.txt")
    reader = DefaultSampleFileReader(results_per_page=50)
    patterns = reader.get_expected_patterns()
    assert patterns
    table, messages = parse_isa_table_sheet_from_fs(
        file_path, expected_patterns=patterns
    )
    assert table
    assert not messages


def test_parse_isa_table_sheet_from_fs_valid_sample_02():
    file_path = pathlib.Path("tests/test-data/MTBLS9999998/s_MTBLS9999998.txt")
    file_path_output = pathlib.Path("test-temp/MTBLS9999998")
    output_sample_file_path = file_path_output / pathlib.Path("s_MTBLS9999998.txt")
    os.makedirs(str(file_path_output), exist_ok=True)
    shutil.copy(file_path, output_sample_file_path)
    reader = DefaultSampleFileReader(results_per_page=50)
    patterns = reader.get_expected_patterns()
    assert patterns
    table, messages = parse_isa_table_sheet_from_fs(
        output_sample_file_path,
        expected_patterns=patterns,
        remove_empty_rows=True,
    )
    assert table
    assert messages
    writer = Writer.get_sample_file_writer()
    result = writer.save_isa_table(
        file_path=str(output_sample_file_path),
        file_sha256_hash=table.sha256_hash,
        isa_table=table.table,
    )
    assert result.success


def test_parse_isa_table_sheet_from_fs_invalid_columns_01():
    file_path = pathlib.Path(
        "tests/test-data/isa-table-files/s_MTBLS1_invalid_columns.txt"
    )
    patterns = DefaultSampleFileReader.patterns
    isa_table, messages = parse_isa_table_sheet_from_fs(
        file_path, expected_patterns=patterns
    )
    assert isa_table
    assert messages

    additional_columns = [
        x
        for x in isa_table.table.headers
        if x.column_structure == ColumnsStructure.ADDITIONAL_COLUMN
    ]
    invalid_ontology_columns = [
        x
        for x in isa_table.table.headers
        if x.column_structure == ColumnsStructure.INVALID_MULTI_COLUMN
    ]
    assert additional_columns
    assert invalid_ontology_columns


def test_parse_isa_table_sheet_from_fs_invalid_columns_02():
    file_path = pathlib.Path(
        "tests/test-data/isa-table-files/m_invalid_cell_context.txt"
    )
    patterns = DefaultAssignmentFileReader.patterns
    isa_table, messages = parse_isa_table_sheet_from_fs(
        file_path, expected_patterns=patterns
    )
    assert isa_table
    assert messages


def test_parse_isa_table_sheet_from_fs_invalid_columns_03():
    file_path = pathlib.Path(
        "tests/test-data/isa-table-files/m_invalid_cell_context_2.txt"
    )

    temp_root_path = ".test-temp"
    temp_path = f"{temp_root_path}/parse-file-{uuid.uuid4()}"
    os.makedirs(temp_path, exist_ok=True)

    try:
        temp_file_path = os.path.join(temp_path, os.path.basename(file_path))
        shutil.copy2(file_path, temp_file_path)
        patterns = DefaultAssignmentFileReader.patterns
        isa_table, messages = parse_isa_table_sheet_from_fs(
            temp_file_path,
            expected_patterns=patterns,
            remove_empty_rows=True,
            remove_new_lines_in_cells=True,
        )
        assert isa_table
        assert len(messages) >= 2
        for item in messages:
            assert "Removed" in item.short
    except Exception as e:
        raise e
    finally:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path, ignore_errors=True)


def test_parse_isa_table_sheet_from_fs_valid_assignment_01():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/m_MTBLS1_metabolite_profiling_NMR_spectroscopy_v2_maf.tsv"
    )
    assignment_file_reader = DefaultAssignmentFileReader()
    table, messages = parse_isa_table_sheet_from_fs(
        file_path, expected_patterns=assignment_file_reader.get_expected_patterns()
    )
    assert table
    assert not messages


def test_parse_isa_table_sheet_012():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/m_MTBLS1_metabolite_profiling_NMR_spectroscopy_v2_maf.tsv"
    )
    assignment_file_reader = DefaultAssignmentFileReader()
    table, messages = parse_isa_table_sheet_from_fs(
        file_path, expected_patterns=assignment_file_reader.get_expected_patterns()
    )
    assert table
    assert not messages


class MockParser(object):
    def __init__(self) -> None:
        self.counter = 0

    def parser_unidecode_error(self, f, messages):
        self.counter += 1
        if self.counter < 2:
            raise UnicodeDecodeError("utf-8", b"", -1, -1, "")
        raise Exception()

    def parser_exception(self, f, messages):
        raise Exception()


def test_parse_isa_file_content_errors_01():
    file_path = "tests/test-data/MTBLS1/m_MTBLS1_metabolite_profiling_NMR_spectroscopy_v2_maf.tsv"
    messages: List[str] = []
    mock_parser = MockParser()
    table, messages = parse_isa_file_content(
        mock_parser.parser_unidecode_error,
        file_path,
        messages=messages,
        fix_unicode_exceptions=False,
    )

    assert not table
    assert messages
    mock_parser = MockParser()
    messages: List[str] = []
    table, messages = parse_isa_file_content(
        mock_parser.parser_unidecode_error,
        file_path,
        messages=messages,
        fix_unicode_exceptions=True,
    )

    assert not table
    assert messages
    mock_parser = MockParser()
    messages: List[str] = []
    table, messages = parse_isa_file_content(
        mock_parser.parser_exception, "", messages=messages, fix_unicode_exceptions=True
    )

    assert not table
    assert messages


def test_parse_isa_table_sheet_from_fs_invalid_01():
    file_path = "tests/test-data/investigation-files/i_Investigation.txt"

    table, messages = parse_isa_table_sheet_from_fs("")
    assert table
    assert not table.file_path
    assert messages

    table, messages = parse_isa_table_sheet_from_fs("/x/td")
    assert table
    assert not table.file_path
    assert messages

    table, messages = parse_isa_table_sheet_from_fs(file_path)
    assert table
    assert not table.file_path
    assert messages

    maf_file_path = "tests/test-data/MTBLS1/m_MTBLS1_metabolite_profiling_NMR_spectroscopy_v2_maf.tsv"
    basename = os.path.basename(maf_file_path)
    table, messages = parse_isa_table_sheet_from_fs(maf_file_path)
    assert table
    assert table.file_path == basename
    assert not messages
