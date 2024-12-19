import pathlib

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.isatab.writer import IsaTableFileWriter
from metabolights_utils.tsv.filter import FilterOperation, TsvFileFilterOption
from metabolights_utils.tsv.sort import SortType, TsvFileSortOption


def test_sample_metadata_file_success_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/s_MTBLS1.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    # with default results_per_page value - 100
    page_count: int = helper.get_total_pages(file_buffer_or_path=file_path)
    assert page_count == 2

    page_count = helper.get_total_pages(
        file_buffer_or_path=file_path, results_per_page=20
    )
    assert page_count == 7

    total_rows_count = helper.get_total_row_count(file_buffer_or_path=file_path)
    assert total_rows_count == 132

    result: IsaTableFileReaderResult = helper.get_headers(file_buffer_or_path=file_path)
    assert len(result.parser_report.messages) == 0

    result: IsaTableFileReaderResult = helper.get_rows(
        file_buffer_or_path=file_path, limit=88
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 88

    result: IsaTableFileReaderResult = helper.get_rows(
        file_buffer_or_path=file_path, offset=100, limit=88
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 32

    result: IsaTableFileReaderResult = helper.get_page(
        page=2, file_buffer_or_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 32

    result: IsaTableFileReaderResult = helper.get_page(
        page=2, results_per_page=50, file_buffer_or_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50

    result: IsaTableFileReaderResult = helper.get_page(
        page=2,
        results_per_page=50,
        file_buffer_or_path=file_path,
        selected_columns=["Sample Name", "Characteristics[Organism part]"],
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50
    assert len(result.isa_table_file.table.columns) == 4


def test_sample_metadata_file_success_02():
    file_path = pathlib.Path("tests/test-data/MTBLS1/s_MTBLS1.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    # with default results_per_page value - 100
    with open(file_path, "r", encoding="utf-8") as file_buffer:
        page_count: int = helper.get_total_pages(file_buffer_or_path=file_buffer)
        assert page_count == 2

    with open(file_path, "r", encoding="utf-8") as file_buffer:
        page_count = helper.get_total_pages(
            file_buffer_or_path=file_buffer, results_per_page=20
        )
        assert page_count == 7

    with open(file_path, "r", encoding="utf-8") as file_buffer:
        total_rows_count = helper.get_total_row_count(file_buffer_or_path=file_buffer)
        assert total_rows_count == 132
    with open(file_path, "r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_headers(
            file_buffer_or_path=file_buffer
        )
        assert len(result.parser_report.messages) == 0

    with open(file_path, "r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_rows(
            file_buffer_or_path=file_buffer, limit=88
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 88

    with open(file_path, "r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_rows(
            file_buffer_or_path=file_buffer,
            offset=100,
            limit=88,
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 32
    with open(file_path, "r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer_or_path=file_buffer, page=2
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 32

    with open(file_path, "r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer_or_path=file_buffer, page=2, results_per_page=50
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 50

    with open(file_path, "r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer_or_path=file_buffer,
            page=2,
            results_per_page=50,
            selected_columns=[
                "Sample Name",
                "Characteristics[Organism part]",
                "Characteristics[Organism]",
            ],
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 50
        assert len(result.isa_table_file.table.columns) == 7


def test_sample_metadata_file_success_03():
    """
    Test file_path with str type and file_buffer
    """
    file_path = pathlib.Path("tests/test-data/MTBLS1/s_MTBLS1.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    # with default results_per_page value - 100

    with open(file_path, "r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer_or_path=file_buffer,
            page=2,
            results_per_page=50,
            selected_columns=[
                "Sample Name",
                "Characteristics[Organism]",
                "Characteristics[Organism part]",
                "Term Source REF.1",
                "Term Accession Number.1",
            ],
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 50
        assert len(result.isa_table_file.table.columns) == 7


def test_sample_metadata_file_success_04():
    """
    Test file_path input with str type
    """
    file_path = pathlib.Path("tests/test-data/MTBLS1/s_MTBLS1.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    # with default results_per_page value - 100
    result: IsaTableFileReaderResult = helper.get_page(
        file_buffer_or_path=file_path,
        page=2,
        results_per_page=50,
        selected_columns=[
            "Sample Name",
            "Characteristics[Organism]",
            "Characteristics[Organism part]",
            "Term Source REF.1",
            "Term Accession Number.1",
        ],
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50
    assert len(result.isa_table_file.table.columns) == 7


def test_sample_metadata_file_invalid_input_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/s_MTBLS1.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()

    result: IsaTableFileReaderResult = helper.get_rows(
        file_buffer_or_path=file_path, offset=150
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 0

    result: IsaTableFileReaderResult = helper.get_page(
        page=10, results_per_page=50, file_buffer_or_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 0

    result: IsaTableFileReaderResult = helper.get_page(
        page=2,
        results_per_page=50,
        file_buffer_or_path=file_path,
        selected_columns=[
            "Sample Name",
            "Invalid Column Name",
            "Metabolite Assignment File",
        ],
    )
    assert len(result.parser_report.messages) == 1
    assert result.isa_table_file.table.row_count == 0
    assert len(result.isa_table_file.table.columns) == 0


def test_with_filter_and_sort_option():
    selected_columns = [
        "Sample Name",
        "Characteristics[Organism]",
        "Characteristics[Organism part]",
        "Term Source REF.1",
        "Term Accession Number.1",
    ]

    filter_options = [
        TsvFileFilterOption(
            search_columns=["Sample Name"],
            operation=FilterOperation.STARTSWITH,
            parameter="ADG19007u_3",
        ),
        TsvFileFilterOption(
            search_columns=["Factor Value[Gender]"],
            operation=FilterOperation.EQUAL,
            parameter="Male",
        ),
    ]

    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Metabolic syndrome]",
            column_sort_type=SortType.STRING,
            reverse=False,
        ),
        TsvFileSortOption(column_name="Sample Name", reverse=True),
    ]
    file_path = pathlib.Path("tests/test-data/MTBLS1/s_MTBLS1.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=50,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 7
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=50,
        file_buffer_or_path=file_path,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50


def test_sample_metadata_file_success_05():
    helper: IsaTableFileWriter = Writer.get_sample_file_writer()
    assert helper
