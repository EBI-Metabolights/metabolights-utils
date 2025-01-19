import datetime
import random
import shutil
from pathlib import Path
from typing import List, Tuple, Union
from unittest import mock

import pytest
from pydantic import BaseModel
from pytest_mock import MockerFixture

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
    download_file_from_rest_api,
    find_assay_technique,
    get_unique_file_extensions,
    rest_api_get,
    rest_api_post,
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


class MockHttpResponse(BaseModel):
    status_code: int = 200
    text: str = ""
    json_data: str = {}


def test_rest_api_get_01(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.get",
        return_value=MockHttpResponse(
            status_code=200, text='{"filename": "a_str.txt", "maf": "m_str.tsv"}'
        ),
    )
    test_url = "/valid/url"
    data, message = rest_api_get(url=test_url)
    assert data and "filename" in data


def test_rest_api_get_02(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.get",
        return_value=MockHttpResponse(
            status_code=400, text='{"filename": "a_str.txt", "maf": "m_str.tsv"}'
        ),
    )
    test_url = "/valid/url"
    data, message = rest_api_get(url=test_url)
    assert not data
    assert message


def test_rest_api_get_03(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.get",
        side_effect=TypeError("Invalid url."),
    )
    test_url = "/valid/url"
    data, message = rest_api_get(url=test_url)
    assert not data
    assert "Invalid url" in message


def test_rest_api_post_01(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.post",
        return_value=MockHttpResponse(
            status_code=200, text='{"filename": "a_str.txt", "maf": "m_str.tsv"}'
        ),
    )
    test_url = "/valid/url"
    data, message = rest_api_post(url=test_url)
    assert data and "filename" in data


def test_rest_api_post_02(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.post",
        return_value=MockHttpResponse(
            status_code=400, text='{"filename": "a_str.txt", "maf": "m_str.tsv"}'
        ),
    )
    test_url = "/valid/url"
    data, message = rest_api_post(url=test_url)
    assert not data
    assert message


def test_rest_api_post_03(mocker: MockerFixture):
    mocker.patch(
        "metabolights_utils.provider.submission_repository.httpx.post",
        side_effect=TypeError("Invalid url."),
    )
    test_url = "/valid/url"
    data, message = rest_api_post(url=test_url)
    assert not data
    assert "Invalid url" in message


class DownloadResponse:
    def __init__(self, status_code: int, file_path: str) -> None:
        self.status_code = status_code
        self.file_path = file_path

    def iter_bytes(self):
        with Path(self.file_path).open("rb") as f:
            yield f.read()

    def raise_for_status(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass


def test_download_file_from_rest_api_01(mocker: MockerFixture):
    file_path = "tests/test-data/rest-api-test-data/s_MTBLS1.txt.zip"
    shutil.rmtree("test-temp/donwload_test", ignore_errors=True)
    dir_path = Path("test-temp/donwload_test")
    local_file_path = dir_path / Path(
        f"download_test_{random.randint(1000000, 9999999)}_tmp.zip"
    )
    dir_path.mkdir(parents=True, exist_ok=True)
    try:
        response = DownloadResponse(status_code=200, file_path=file_path)
        mocker.patch(
            "metabolights_utils.provider.submission_repository.httpx.stream",
            return_value=response,
        )
        timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp() - 10000
        test_url = "/valid/url"
        success, message = download_file_from_rest_api(
            local_file_path=local_file_path,
            url=test_url,
            is_zip_response=True,
            modification_time=timestamp,
        )
        assert (dir_path / Path("s_MTBLS1.txt")).exists()
        assert success

        shutil.rmtree(str(dir_path), ignore_errors=True)
        dir_path.mkdir(parents=True, exist_ok=True)
        success, message = download_file_from_rest_api(
            local_file_path=str(local_file_path),
            url=test_url,
            is_zip_response=False,
            modification_time=timestamp,
        )
        assert local_file_path.exists()
        assert success

        shutil.rmtree(str(dir_path), ignore_errors=True)
        dir_path.mkdir(parents=True, exist_ok=True)

        def raise_exception():
            raise TimeoutError("Timeout error")

        response.iter_bytes = raise_exception
        success, message = download_file_from_rest_api(
            local_file_path=local_file_path,
            url=test_url,
            is_zip_response=False,
            modification_time=timestamp,
        )
        assert not local_file_path.exists()
        assert not success
        assert "Timeout error" in message

    finally:
        if dir_path.exists():
            shutil.rmtree(str(dir_path), ignore_errors=True)
