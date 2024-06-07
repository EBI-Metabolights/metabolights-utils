from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.default.base_isa_table_file import BaseIsaTableFileReader
from metabolights_utils.isatab.reader import InvestigationFileReader
from metabolights_utils.isatab.writer import InvestigationFileWriter, IsaTableFileWriter


def test_reader_01():
    reader = Reader.get_investigation_file_reader()
    assert isinstance(reader, InvestigationFileReader)

    reader = Reader.get_sample_file_reader(results_per_page=10)
    assert isinstance(reader, BaseIsaTableFileReader)
    patterns = reader.get_expected_patterns()
    assert patterns

    reader = Reader.get_assay_file_reader(results_per_page=10)
    assert isinstance(reader, BaseIsaTableFileReader)
    patterns = reader.get_expected_patterns()
    assert patterns

    reader = Reader.get_assignment_file_reader(results_per_page=10)
    assert isinstance(reader, BaseIsaTableFileReader)
    patterns = reader.get_expected_patterns()
    assert patterns


def test_writer_01():
    writer = Writer.get_investigation_file_writer()
    assert isinstance(writer, InvestigationFileWriter)

    writer = Writer.get_assay_file_writer()
    assert isinstance(writer, IsaTableFileWriter)

    writer = Writer.get_sample_file_writer()
    assert isinstance(writer, IsaTableFileWriter)

    writer = Writer.get_assignment_file_writer()
    assert isinstance(writer, IsaTableFileWriter)
