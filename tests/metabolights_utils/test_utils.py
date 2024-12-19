import pytest

from metabolights_utils.common import sort_by_study_id

valid_study_ids = [
    "MTBLS10222",
    "mtbls10222",
    "mtbls1",
    "mtbls10",
]
invalid_study_ids = [
    None,
    "",
    "mtbs1",
    "mtbls-10",
    "mtbls10.0",
    "mtbls-10.0",
]


@pytest.mark.parametrize("study_id", valid_study_ids)
def test_sort_by_study_id_01(study_id: str):
    actual = sort_by_study_id(study_id)
    assert actual > 0


@pytest.mark.parametrize("study_id", invalid_study_ids)
def test_sort_by_study_id_02(study_id: str):
    actual = sort_by_study_id(study_id)
    assert actual == -1
