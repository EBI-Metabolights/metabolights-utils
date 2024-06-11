from typing import List, Tuple, Union
from unittest import mock

import pytest

from metabolights_utils.models.common import GenericMessage
from metabolights_utils.models.metabolights.model import (
    CurationRequest,
    MetabolightsStudyModel,
    StudyDBMetadata,
    StudyFolderMetadata,
    StudyStatus,
    Submitter,
    UserRole,
    UserStatus,
)
from metabolights_utils.provider.local_folder_metadata_collector import (
    LocalFolderMetadataCollector,
)
from metabolights_utils.provider.study_provider import (
    AbstractDbMetadataCollector,
    AbstractFolderMetadataCollector,
    MetabolightsStudyProvider,
)


def test_load_study_data_with_default_paramters_01():
    provider = MetabolightsStudyProvider()
    model: MetabolightsStudyModel = provider.load_study(
        "MTBLS1", "tests/test-data/MTBLS1"
    )
    assert model
    assert model.has_investigation_data == True
    assert model.has_sample_table_data == False
    assert model.has_assay_table_data == False
    assert model.has_assignment_table_data == False
    assert model.has_db_metadata == False
    assert model.has_folder_metadata == False
    assert model.investigation.studies
    assert model.investigation.studies[0].identifier == "MTBLS1"
    assert len(model.assays) == 1


test_studies = [
    ("MTBLS1", "tests/test-data/MTBLS1"),
    ("MTBLS227", "tests/test-data/MTBLS227"),
    ("MTBLS2028", "tests/test-data/MTBLS2028"),
]


test_studies_with_files = [
    ("MTBLS4861", "tests/test-data/MTBLS4861"),
    ("MTBLS5195", "tests/test-data/MTBLS5195"),
]


@pytest.mark.parametrize("study_id,study_path", test_studies)
def test_load_study_data_02(study_id, study_path):
    provider = MetabolightsStudyProvider()
    model: MetabolightsStudyModel = provider.load_study(
        study_id,
        study_path,
        load_assay_files=True,
        load_sample_file=True,
        load_maf_files=True,
    )
    assert model
    assert model.has_investigation_data == True
    assert model.has_sample_table_data == True
    assert model.has_assay_table_data == True
    assert model.has_assignment_table_data == True
    assert model.has_db_metadata == False
    assert model.has_folder_metadata == False
    assert model.investigation.studies
    assert model.investigation.studies[0].identifier == study_id
    assert len(model.assays) >= 1


@pytest.mark.parametrize("study_id,study_path", test_studies)
def test_load_study_data_03(study_id, study_path):
    provider = MetabolightsStudyProvider()
    model: MetabolightsStudyModel = provider.load_study(
        study_id,
        study_path,
        load_assay_files=True,
        load_sample_file=True,
        load_maf_files=True,
        assignment_sheet_limit=1,
        samples_sheet_limit=1,
        assay_sheet_limit=1,
    )
    assert model
    assert model.has_investigation_data == True
    assert model.has_sample_table_data == True
    assert model.has_assay_table_data == True
    assert model.has_assignment_table_data == True
    assert model.has_db_metadata == False
    assert model.has_folder_metadata == False
    assert model.investigation.studies
    assert model.investigation.studies[0].identifier == study_id
    assert len(model.assays) >= 1
    assert list(model.assays.values())[0].table.row_count == 1


@pytest.mark.parametrize("study_id,study_path", test_studies_with_files)
def test_load_study_data_04(study_id, study_path):
    class DefaultFolderMetadataCollector(AbstractFolderMetadataCollector):
        def get_folder_metadata(
            self,
            study_path,
            calculate_data_folder_size: bool = False,
            calculate_metadata_size: bool = False,
        ) -> Tuple[Union[StudyFolderMetadata, None], List[GenericMessage]]:
            return (
                StudyFolderMetadata(
                    folder_size_in_bytes=1024, folder_size_in_str="1.00 KB"
                ),
                [],
            )

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
        folder_metadata_collector=DefaultFolderMetadataCollector(),
        db_metadata_collector=DefaultDbMetadataCollector(),
    )
    connection = mock.Mock()
    model: MetabolightsStudyModel = provider.load_study(
        study_id,
        study_path,
        connection=connection,
        load_assay_files=True,
        load_sample_file=True,
        load_maf_files=True,
        load_folder_metadata=True,
        calculate_data_folder_size=True,
        calculate_metadata_size=True,
    )
    assert model
    assert model.has_investigation_data == True
    assert model.has_sample_table_data == True
    assert model.has_assay_table_data == True
    assert model.has_assignment_table_data == True
    assert model.has_db_metadata == True
    assert model.has_folder_metadata == True
    assert model.investigation.studies
    assert model.investigation.studies[0].identifier == study_id
    assert model.study_folder_metadata
    assert model.study_folder_metadata.folder_size_in_bytes == 1024


@pytest.mark.parametrize("study_id,study_path", test_studies)
def test_load_study_data_05(study_id, study_path):

    provider = MetabolightsStudyProvider()
    model: MetabolightsStudyModel = provider.load_study(
        study_id,
        study_path,
        load_assay_files=False,
        load_sample_file=True,
        load_maf_files=False,
        load_folder_metadata=False,
    )
    assert model
    assert model.has_investigation_data == True
    assert model.has_sample_table_data == True
    assert model.has_assay_table_data == False
    assert model.has_assignment_table_data == False
    assert model.has_db_metadata == False
    assert model.has_folder_metadata == False
    assert model.investigation.studies
    assert model.investigation.studies[0].identifier == study_id
