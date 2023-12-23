import pathlib

from metabolights_utils.isatab.default.assay_file import DefaultAssayFileReader
from metabolights_utils.isatab.default.assignment_file import (
    DefaultAssignmentFileReader,
)
from metabolights_utils.isatab.default.parser.isa_table_parser import (
    parse_isa_table_sheet_from_fs,
)
from metabolights_utils.isatab.default.sample_file import DefaultSampleFileReader


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
    patterns = DefaultSampleFileReader.patterns
    table, messages = parse_isa_table_sheet_from_fs(
        file_path, expected_patterns=patterns
    )
    assert table
    assert not messages


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
