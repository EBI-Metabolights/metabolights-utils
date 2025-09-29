import os
import pathlib
import uuid
from typing import List

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.default.parser.investigation_parser import (
    parse_investigation_file_content,
    parse_investigation_from_fs,
)
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights_utils.isatab.writer import InvestigationFileWriter
from metabolights_utils.models.isa.investigation_file import (
    ExtendedOntologyAnnotation,
    Funder,
)
from metabolights_utils.models.parser.common import ParserMessage
from metabolights_utils.utils.hash_utils import MetabolightsHashUtils as HashUtils


def test_parse_investigation_from_fs_valid_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    investigation, messages = parse_investigation_from_fs(file_path)
    assert investigation
    assert not messages


def test_parse_investigation_from_fs_valid_02_comments():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_MTBLS74.txt"
    )
    investigation, messages = parse_investigation_from_fs(file_path)
    assert investigation
    assert not messages


def test_parse_investigation_from_fs_valid_03_comments():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_MTBLS74.txt"
    )
    investigation, messages = parse_investigation_from_fs(file_path)
    # Writer.get_investigation_file_writer().write(
    #     investigation,
    #     file_buffer_or_path=pathlib.Path("i_Investigation_MTBLS74_01.txt"),
    #     values_in_quotation_mark=False,
    # )

    for idx, assay in enumerate(investigation.studies[0].study_assays.assays, start=1):
        assay.assay_identifier = f"Test 2-{idx}"
        assay.assay_type.term = f"Test-{idx}"
        assay.assay_descriptors[0].term = f"Test-term-{idx}"
        assay.assay_descriptors.append(
            ExtendedOntologyAnnotation(
                term="Test-new", category="test-new", source="test-new"
            )
        )
        assay.result_file_format = "MAF v2.0"
    for idx, design in enumerate(
        investigation.studies[0].study_design_descriptors.design_types, start=1
    ):
        design.category = f"test-{idx}"
    for idx, person in enumerate(
        investigation.studies[0].study_contacts.people, start=1
    ):
        person.orcid = f"test-orcid-{idx}"
        person.additional_emails = [f"test-{idx}-1", f"test-{idx}-2"]
    investigation.studies[0].funders[0].grant_ids = ["test1", "test2"]
    investigation.studies[0].study_factors.factors[0].column_format = "test-format"
    investigation.sync_comments_from_fields()
    # Writer.get_investigation_file_writer().write(
    #     investigation,
    #     file_buffer_or_path=pathlib.Path("i_Investigation_MTBLS74_02.txt"),
    #     values_in_quotation_mark=False,
    #     sync_comments_from_fields=True,
    # )
    assert (
        investigation.studies[0].study_assays.assays[0].assay_identifier == "Test 2-1"
    )
    assert (
        investigation.studies[0].study_design_descriptors.design_types[0].category
        == "test-1"
    )
    assert investigation
    assert not messages


def test_parse_investigation_from_fs_valid_04_comments():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    investigation, messages = parse_investigation_from_fs(file_path)
    # Writer.get_investigation_file_writer().write(
    #     investigation,
    #     file_buffer_or_path=pathlib.Path("i_Investigation_MTBLS1_01.txt"),
    #     values_in_quotation_mark=False,
    #     sync_comments_from_fields=True,
    # )

    study = investigation.studies[0]
    assay = study.study_assays.assays[0]
    person = study.study_contacts.people[0]
    descriptor = study.study_design_descriptors.design_types[0]
    factor = study.study_factors.factors[0]
    factor.column_format = "ontology"
    descriptor.category = "disease"
    person.affiliation_ror_id = "https://ror.org/02catss52"
    person.orcid = "10000-10000"
    person.additional_emails = []
    assay.assay_identifier = f"{study.identifier}-01"
    assay.assay_descriptors.append(ExtendedOntologyAnnotation(term="MS/MS"))
    assay.result_file_format = "MAF v2.0"
    investigation.studies[0].funders.append(
        Funder(
            funder_name="Test Funder",
            funder_id="xxx",
            grant_ids=["grant1", "grant2", "grant3"],
        )
    )

    # Writer.get_investigation_file_writer().write(
    #     investigation,
    #     file_buffer_or_path=pathlib.Path("i_Investigation_MTBLS1_02.txt"),
    #     values_in_quotation_mark=False,
    #     sync_comments_from_fields=True,
    # )
    investigation.sync_comments_from_fields()
    # 1 identifier + result file + 5 assay descriptor
    assert len(study.study_assays.comments) == 7
    assert len(study.study_contacts.comments) == 2
    assert len(study.study_design_descriptors.comments) == 2
    assert len(study.study_factors.comments) == 1
    study.study_assays.comments[0].value[0] == f"{study.identifier}-01"
    assert len(study.comments) == 3

    assert investigation
    assert not messages


def test_parse_investigation_from_fs_invalid_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/xi_Investigation.txt")
    investigation, messages = parse_investigation_from_fs(file_path)
    assert not investigation
    assert messages


def test_parse_investigation_from_fs_invalid_02():
    file_path = pathlib.Path("tests/test-data/investigation-files/i_Investigation.txt")
    investigation, messages = parse_investigation_from_fs(file_path)
    assert not investigation
    assert messages


def test_parse_investigation_from_fs_invalid_03():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_empty_lines.txt"
    )
    investigation, messages = parse_investigation_from_fs(file_path)
    assert investigation
    assert messages


def test_investigation_file_read_write_success_1():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)
    assert len(result.investigation.studies) == 1
    sha25_hash = result.sha256_hash

    tmp_file_name = uuid.uuid4().hex
    tmp_path = pathlib.Path(f"test-temp/test_{tmp_file_name}.txt")
    try:
        writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
        writer.write(
            result.investigation,
            file_buffer_or_path=tmp_path,
            values_in_quotation_mark=True,
        )
        new_sha256 = HashUtils.sha256sum(tmp_path)

        assert new_sha256 == sha25_hash
        writer.write(
            result.investigation,
            file_buffer_or_path=tmp_path,
            values_in_quotation_mark=False,
        )
        new_sha256 = HashUtils.sha256sum(tmp_path)
        assert new_sha256 != sha25_hash
    except Exception as exc:
        raise exc
    finally:
        os.remove(tmp_path)


def parser_unidecode_error(f, file_path, messages):
    raise UnicodeDecodeError("utf-8", b"", -1, -1, "")


def parser_exception(f, file_path, messages):
    raise Exception()


def test_parse_investigation_from_fs_invalid_04():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_invalid.txt"
    )

    messages: List[ParserMessage] = []
    investigation, messages = parse_investigation_file_content(
        parser=parser_unidecode_error,
        file_path=file_path,
        messages=messages,
        fix_unicode_exceptions=False,
    )
    assert not investigation
    assert messages

    messages = []
    investigation, messages = parse_investigation_file_content(
        parser=parser_unidecode_error,
        file_path=file_path,
        messages=messages,
        fix_unicode_exceptions=True,
    )
    assert not investigation
    assert messages

    messages = []
    investigation, messages = parse_investigation_file_content(
        parser=parser_exception,
        file_path=file_path,
        messages=messages,
        fix_unicode_exceptions=True,
    )
    assert not investigation
    assert messages


def test_parse_investigation_from_fs_invalid_05():
    file_path = pathlib.Path(
        "tests/test-data/investigation-files/i_Investigation_invalid_content.txt"
    )
    investigation, messages = parse_investigation_from_fs(file_path)
    assert investigation
    assert messages
