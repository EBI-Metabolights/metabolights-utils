import pathlib

from metabolights_utils.isa_metadata import AssayFileReader, AssignmentFileReader, SampleFileReader


def test_assay_file_reader_success_01():
    file_path = pathlib.Path("tests/test_data/a_MTBLS1_assay.txt")
    file_reader = AssayFileReader(file_path=file_path.absolute())

    page_count = file_reader.get_total_pages()
    assert page_count == 2
    total_rows_count = file_reader.get_total_row_count()
    isa_file, messages = file_reader.get_file_headers()
    assert len(messages) == 0
    assert isa_file.table.totalRowCount == total_rows_count
    isa_file, messages = file_reader.get_file_rows(number_of_rows=88)
    assert len(messages) == 0
    assert isa_file.table.rowCount == 88
    isa_file, messages = file_reader.get_file_rows(row_offset=77)
    assert len(messages) == 0
    assert isa_file.table.rowOffset == 77

    isa_file, messages = file_reader.get_page(2, 50)
    assert len(messages) == 0

    isa_file, messages = file_reader.get_page(2, 100)
    assert len(messages) == 0

    isa_file, messages = file_reader.get_page(2, 200)
    assert len(messages) == 0

    isa_file, messages = file_reader.get_page(4, 33)
    assert len(messages) == 0


def test_sample_file_reader_success_01():
    file_path = pathlib.Path("tests/test_data/s_MTBLS1.txt")
    file_reader = SampleFileReader(file_path=file_path.absolute())
    isa_file, messages = file_reader.get_page(10, 10)

    assert isa_file.table.rowOffset == 90
    assert len(messages) == 0
    column_names = ["Source Name", "Characteristics[Organism]"]
    isa_file, messages = file_reader.get_page(1, 100, column_names=column_names)
    assert len(isa_file.table.headers) == 2
    assert isa_file.table.rowCount == 100


def test_assignment_file_reader_success_01():
    file_path = pathlib.Path("tests/test_data/m_MTBLS1_assignment.tsv")
    file_reader = AssignmentFileReader(file_path=file_path.absolute())
    isa_file, messages = file_reader.get_page(10, 10)

    assert isa_file.table.rowOffset == 90
    assert len(messages) == 0
    column_names = ["database_identifier", "chemical_formula"]
    isa_file, messages = file_reader.get_page(1, 100, column_names=column_names)
    assert len(isa_file.table.headers) == 2
    assert isa_file.table.rowCount == 100
