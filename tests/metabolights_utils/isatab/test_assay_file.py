import pathlib

from metabolights_utils.isatab.isa_table_file_reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.isatab.isatab_file_helper import IsaTabFileHelper
from metabolights_utils.models.isa.common import (
    FilterOperation,
    SortType,
    TsvFileFilterOption,
    TsvFileSortOption,
)


def test_assay_metadata_file_success_01():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = IsaTabFileHelper.get_assay_file_reader()
    # with default results_per_page value - 100
    page_count: int = helper.get_total_pages(file_path=file_path)
    assert page_count == 2

    page_count = helper.get_total_pages(file_path=file_path, results_per_page=20)
    assert page_count == 7

    total_rows_count = helper.get_total_row_count(file_path=file_path)
    assert total_rows_count == 132

    result: IsaTableFileReaderResult = helper.get_headers(file_path=file_path)
    assert len(result.parser_report.messages) == 0

    result: IsaTableFileReaderResult = helper.get_rows(file_path=file_path, limit=88)
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 88

    result: IsaTableFileReaderResult = helper.get_rows(file_path=file_path, offset=100, limit=88)
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 32

    result: IsaTableFileReaderResult = helper.get_page(page=2, file_path=file_path)
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 32

    result: IsaTableFileReaderResult = helper.get_page(
        page=2, results_per_page=50, file_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 50

    result: IsaTableFileReaderResult = helper.get_page(
        page=2,
        results_per_page=50,
        file_path=file_path,
        selected_columns=[
            "Sample Name",
            "Derived Spectral Data File",
            "Metabolite Assignment File",
        ],
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 50
    assert len(result.isa_table_file.table.columns) == 3


def test_assay_metadata_file_success_02():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = IsaTabFileHelper.get_assay_file_reader()
    # with default results_per_page value - 100
    with open(file_path, "r") as file_buffer:
        page_count: int = helper.get_total_pages(file_buffer=file_buffer)
        assert page_count == 2

    with open(file_path, "r") as file_buffer:
        page_count = helper.get_total_pages(file_buffer=file_buffer, results_per_page=20)
        assert page_count == 7

    with open(file_path, "r") as file_buffer:
        total_rows_count = helper.get_total_row_count(file_buffer=file_buffer)
        assert total_rows_count == 132
    with open(file_path, "r") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_headers(file_buffer=file_buffer)
        assert len(result.parser_report.messages) == 0

    with open(file_path, "r") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_rows(
            file_buffer=file_buffer, file_path=file_path, limit=88
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.rowCount == 88

    with open(file_path, "r") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_rows(
            file_buffer=file_buffer, file_path=file_path, offset=100, limit=88
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.rowCount == 32
    with open(file_path, "r") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer=file_buffer, page=2, file_path=file_path
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.rowCount == 32

    with open(file_path, "r") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer=file_buffer, page=2, results_per_page=50, file_path=file_path
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.rowCount == 50

    with open(file_path, "r") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer=file_buffer,
            page=2,
            results_per_page=50,
            file_path=file_path,
            selected_columns=[
                "Sample Name",
                "Derived Spectral Data File",
                "Metabolite Assignment File",
            ],
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.rowCount == 50
        assert len(result.isa_table_file.table.columns) == 3


def test_assay_metadata_file_success_03():
    """
    Test file_path with str type and file_buffer
    """
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = IsaTabFileHelper.get_assay_file_reader()
    # with default results_per_page value - 100

    with open(file_path, "r") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer=file_buffer,
            page=2,
            results_per_page=50,
            file_path=str(file_path),
            selected_columns=[
                "Sample Name",
                "Derived Spectral Data File",
                "Metabolite Assignment File",
            ],
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.rowCount == 50
        assert len(result.isa_table_file.table.columns) == 3


def test_assay_metadata_file_success_04():
    """
    Test file_path input with str type
    """
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = IsaTabFileHelper.get_assay_file_reader()
    # with default results_per_page value - 100
    result: IsaTableFileReaderResult = helper.get_page(
        page=2,
        results_per_page=50,
        file_path=str(file_path),
        selected_columns=[
            "Sample Name",
            "Derived Spectral Data File",
            "Metabolite Assignment File",
        ],
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 50
    assert len(result.isa_table_file.table.columns) == 3


def test_assay_metadata_file_invalid_input_01():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = IsaTabFileHelper.get_assay_file_reader()

    result: IsaTableFileReaderResult = helper.get_rows(file_path=file_path, offset=150)
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 0

    result: IsaTableFileReaderResult = helper.get_page(
        page=10, results_per_page=50, file_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 0

    result: IsaTableFileReaderResult = helper.get_page(
        page=2,
        results_per_page=50,
        file_path=file_path,
        selected_columns=["Sample Name", "Invalid Column Name", "Metabolite Assignment File"],
    )
    assert len(result.parser_report.messages) == 1
    assert result.isa_table_file.table.rowCount == 0
    assert len(result.isa_table_file.table.columns) == 0


def test_with_filter_and_sort_option_01():
    selected_columns = [
        "Sample Name",
        "Protocol REF.2",
        "Parameter Value[Instrument]",
        "Term Source REF.4",
        "Term Accession Number.4",
    ]

    filter_options = [
        TsvFileFilterOption(
            column_name="Sample Name",
            operation=FilterOperation.STARTSWITH,
            parameter="ADG19007u_3",
        ),
        TsvFileFilterOption(
            column_name="Parameter Value[Sample pH]",
            operation=FilterOperation.GREATER,
            parameter=1.0,
        ),
    ]

    sort_options = [
        TsvFileSortOption(column_name="Sample Name", reverse=True),
        TsvFileSortOption(
            column_name="Parameter Value[Sample pH]",
            columncolumn_sort_type=SortType.FLOAT,
            reverse=False,
        ),
    ]
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = IsaTabFileHelper.get_assay_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=50,
        file_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 14
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=50,
        file_path=file_path,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.rowCount == 50
