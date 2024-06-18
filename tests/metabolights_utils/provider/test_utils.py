from typing import List, Tuple, Union
from unittest import mock

import pytest

from metabolights_utils.models.common import GenericMessage
from metabolights_utils.models.metabolights.model import (
    CurationRequest,
    MetabolightsStudyModel,
    StudyDBMetadata,
    StudyStatus,
    Submitter,
    UserRole,
    UserStatus,
)
from metabolights_utils.provider.study_provider import (
    AbstractDbMetadataCollector,
    MetabolightsStudyProvider,
)
from metabolights_utils.provider.utils import (
    find_assay_technique,
    get_unique_file_extensions,
)

assay_names = {
    (
        "MTBLS227",
        "tests/test-data/MTBLS227",
        "a_MTBLS227_assay_A_Profiling.txt",
        "MALDI-MS",
    ),
    ("MTBLS227", "tests/test-data/MTBLS227", "a_MTBLS227_assay_B_LIFT.txt", "MALDI-MS"),
    (
        "MTBLS1755",
        "tests/test-data/MTBLS1755",
        "a_MTBLS1755_CE-MS_positive__metabolite_profiling.txt",
        "CE-MS",
    ),
    (
        "MTBLS1892",
        "tests/test-data/MTBLS1892",
        "a_MTBLS1892_LC-DAD__reverse-phase_metabolite_profiling.txt",
        "LC-DAD",
    ),
    (
        "MTBLS1906",
        "tests/test-data/MTBLS1906",
        "a_MTBLS1906_DI-MS_negative_metabolite_profiling.txt",
        "DI-MS",
    ),
    (
        "MTBLS1892",
        "tests/test-data/MTBLS1892",
        "a_MTBLS1892_GC-MS_positive__metabolite_profiling-1.txt",
        "GC-MS",
    ),
    (
        "MTBLS2028",
        "tests/test-data/MTBLS2028",
        "a_MTBLS2028_Lipid_FIA-MS_metabolite_profiling.txt",
        "FIA-MS",
    ),
    (
        "MTBLS2028",
        "tests/test-data/MTBLS2028",
        "a_MTBLS2028_AA_LC-MS_metabolite_profiling.txt",
        "LC-MS",
    ),
    (
        "MTBLS2060",
        "tests/test-data/MTBLS2060",
        "a_MTBLS2060_NMR___metabolite_profiling.txt",
        "NMR",
    ),
    (
        "MTBLS2075",
        "tests/test-data/MTBLS2075",
        "a_MTBLS2075_MSImaging___metabolite_profiling.txt",
        "MSImaging",
    ),
    (
        "MTBLS60",
        "tests/test-data/MTBLS60",
        "a_MTBLS60_dippA_UPLC_MS.txt",
        "MS",
    ),
}


@pytest.mark.parametrize("study_id,study_path,assay_name,technique_name", assay_names)
def test_find_assay_technique_01(study_id, study_path, assay_name, technique_name):

    class DefaultDbMetadataCollector(AbstractDbMetadataCollector):
        def get_study_metadata_from_db(
            self, study_id: str, connection
        ) -> Tuple[Union[StudyDBMetadata, None], List[GenericMessage]]:
            return (
                StudyDBMetadata(
                    study_id=study_id,
                    status=StudyStatus.get_from_int(3),
                    study_types=["X-Data"],
                    curation_request=CurationRequest.MANUAL_CURATION,
                    submitters=[
                        Submitter(
                            user_name="test",
                            status=UserStatus.get_from_int(2),
                            role=UserRole.get_from_int(1),
                        )
                    ],
                ),
                [],
            )

    provider = MetabolightsStudyProvider(
        db_metadata_collector=DefaultDbMetadataCollector()
    )
    connection = mock.Mock()
    model: MetabolightsStudyModel = provider.load_study(
        study_id, study_path, connection=connection, load_assay_files=True
    )
    assays = model.assays
    if assay_name in assays:
        assay = assays[assay_name]
        technique = find_assay_technique(
            model=model,
            assay_file=assay,
            assay_file_subset=assay,
        )
        assert technique
        assert technique.name == technique_name


filenames = [
    ({"x.mzML", "c.mzML", "d.mzML"}, {".mzml"}),
    ({"x.mzML", "c.mzXML", "d.mzML"}, {".mzml", ".mzxml"}),
    ({"x.wiff.scan", "x.wiff", "y.wiff"}, {".wiff", ".wiff.scan"}),
]


@pytest.mark.parametrize("filenames,expected_set", filenames)
def test_get_unique_file_extension_01(filenames, expected_set):
    actual = get_unique_file_extensions(filenames)
    assert len(actual - expected_set) == 0
