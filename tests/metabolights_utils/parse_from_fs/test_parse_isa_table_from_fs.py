import pathlib

from metabolights_utils.isatab.helper.assay_file_helper import AssayFileHelper
from metabolights_utils.isatab.helper.assignment_file_helper import AssignmentFileHelper
from metabolights_utils.isatab.helper.sample_file_helper import SampleFileHelper
from metabolights_utils.models.isa.parser.isa_table_parser import parse_isa_table_sheet_from_fs


def test_parse_isa_table_sheet_from_fs_valid_assay_01():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    patterns = AssayFileHelper.patterns
    table, messages = parse_isa_table_sheet_from_fs(file_path, expected_patterns=patterns)
    assert table
    assert not messages


def test_parse_isa_table_sheet_from_fs_valid_sample_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/s_MTBLS1.txt")
    patterns = SampleFileHelper.patterns
    table, messages = parse_isa_table_sheet_from_fs(file_path, expected_patterns=patterns)
    assert table
    assert not messages


def test_parse_isa_table_sheet_from_fs_valid_assignment_01():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/m_MTBLS1_metabolite_profiling_NMR_spectroscopy_v2_maf.tsv"
    )
    patterns = AssignmentFileHelper.patterns
    table, messages = parse_isa_table_sheet_from_fs(file_path, expected_patterns=patterns)
    assert table
    assert not messages
