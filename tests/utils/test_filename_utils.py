import pytest

from metabolights_utils.utils.filename_utils import MetabolightsFileNameUtils

fixes = [
    ("test&[value]", "test__value_"),
    ("test value", "test_value"),
    ("test+value", "test_PLUS_value"),
    ("test?value", "test_value"),
    ("test*value", "test_value"),
    ("test%value", "test_value"),
    ("test$value", "test_value"),
    ("test@value", "test_value"),
    ("özgür", "ozgur"),
    ("", ""),
    (" ", ""),
]

no_changes = [
    ("testdata", "testdata"),
    ("i_Investigation.txt", "i_Investigation.txt"),
    ("i_Investigation.txt", "i_Investigation.txt"),
    ("a_LC-MS_hilic.txt", "a_LC-MS_hilic.txt"),
    ("m_LC-MS_hilic.tsv", "m_LC-MS_hilic.tsv"),
    ("m_LC-MS_hilic_01.tsv", "m_LC-MS_hilic_01.tsv"),
    ("sample/i_Investigation.txt", "sample/i_Investigation.txt"),
]


@pytest.mark.parametrize("input_value,expected", no_changes)
def test_sanitise_filename_01(input_value, expected):
    actual = MetabolightsFileNameUtils.sanitise_filename(
        input_value, allow_spaces=False
    )
    assert actual == expected


@pytest.mark.parametrize("input_value,expected", fixes)
def test_sanitise_filename_02(input_value, expected):
    actual = MetabolightsFileNameUtils.sanitise_filename(
        input_value, allow_spaces=False
    )
    assert actual == expected
