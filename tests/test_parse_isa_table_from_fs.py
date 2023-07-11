import pathlib
from metabolights_utils.isa_metadata import AssayFileReader, SampleFileReader

from metabolights_utils.models.isa.parser.isa_table_parser import parse_isa_table_sheet_from_fs


def test_parse_isa_table_sheet_from_fs_valid_assay_01():
    file_path = pathlib.Path("tests/test_data/a_MTBLS1_assay.txt")
    patterns = AssayFileReader.patterns
    table, messages = parse_isa_table_sheet_from_fs(file_path, expected_patterns=patterns)
    assert table
    assert not messages


def test_parse_isa_table_sheet_from_fs_valid_sample_01():
    file_path = pathlib.Path("tests/test_data/s_MTBLS1.txt")
    patterns = SampleFileReader.patterns
    table, messages = parse_isa_table_sheet_from_fs(file_path, expected_patterns=patterns)
    assert table
    assert not messages


def test_parse_isa_table_sheet_from_fs_valid_assignment_01():
    file_path = pathlib.Path("tests/test_data/m_MTBLS1_assignment.tsv")
    table, messages = parse_isa_table_sheet_from_fs(file_path)
    assert table
    assert not messages
