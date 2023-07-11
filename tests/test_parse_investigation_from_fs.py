import pathlib

from metabolights_utils.models.isa.parser.investigation_parser import parse_investigation_from_fs


def test_parse_investigation_from_fs_valid_01():
    file_path = pathlib.Path("tests/test_data/MTBLS1_i_Investigation.txt")
    investigation, messages = parse_investigation_from_fs(file_path)
    assert investigation
    assert not messages
