import os
import pathlib
import uuid
from typing import List

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights_utils.isatab.writer import InvestigationFileWriter
from metabolights_utils.models.isa.common import OntologyItem
from metabolights_utils.models.isa.investigation_file import Assay, Study


def test_investigation_file_read_01():
    file_path = pathlib.Path("tests/test-data/MTBLS398/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)
    assert len(result.investigation.studies) == 1

    study: Study = result.investigation.studies[0]
    assays: List[Assay] = study.study_assays.assays

    assert len(assays) == 40


def test_investigation_file_write_01():
    file_path = pathlib.Path("tests/test-data/MTBLS398/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)

    assay: Assay = result.investigation.studies[0].study_assays.assays[0]
    assay.measurement_type = OntologyItem(
        term="test",
        term_source_ref="test source",
        term_accession_number="test accesion",
    )

    tmp_file_name = uuid.uuid4().hex
    tmp_path = pathlib.Path(f"test-temp/test_{tmp_file_name}.txt")
    writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
    writer.write(result.investigation, file_buffer_or_path=tmp_path)

    result2: InvestigationFileReaderResult = reader.read(file_buffer_or_path=tmp_path)
    assay_read: Assay = result2.investigation.studies[0].study_assays.assays[0]
    assert assay_read.measurement_type.term == "test"
    assert assay_read.measurement_type.term_source_ref == "test source"
    assert assay_read.measurement_type.term_accession_number == "test accesion"
    os.remove(tmp_path)
