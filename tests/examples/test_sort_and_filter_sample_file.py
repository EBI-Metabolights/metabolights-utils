import pathlib

from metabolights_utils.isatab import Reader
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.tsv.filter import FilterOperation, TsvFileFilterOption
from metabolights_utils.tsv.sort import (
    SortType,
    TsvFileSortOption,
    TsvFileSortValueOrder,
)


def test_with_integer_sort_option_01():
    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Replicate]",
            reverse=False,
            column_sort_type=SortType.INTEGER,
            value_order=TsvFileSortValueOrder.INVALID_EMPTY_VALID,
        ),
    ]

    file_path = pathlib.Path("tests/test-data/test-data-01/s_sample_with_types.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 100

    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Replicate]",
            reverse=False,
            column_sort_type=SortType.INTEGER,
            value_order=TsvFileSortValueOrder.EMPTY_INVALID_VALID,
        )
    ]

    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 100

    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Replicate]",
            reverse=True,
            column_sort_type=SortType.INTEGER,
            value_order=TsvFileSortValueOrder.VALID_EMPTY_INVALID,
        )
    ]

    result: IsaTableFileReaderResult = helper.get_page(
        page=82,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 67


def test_with_float_sort_option_01():
    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Population ID]",
            column_sort_type=SortType.FLOAT,
            value_order=TsvFileSortValueOrder.VALID_EMPTY_INVALID,
            reverse=False,
        ),
    ]

    file_path = pathlib.Path("tests/test-data/test-data-01/s_sample_with_types.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=82,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 67

    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Population ID]",
            column_sort_type=SortType.FLOAT,
            value_order=TsvFileSortValueOrder.INVALID_EMPTY_VALID,
            reverse=False,
        ),
    ]
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 100


def test_with_datetime_sort_option_01():
    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Date]",
            column_sort_type=SortType.DATETIME,
            default_datetime_pattern="%d/%m/%Y",
            value_order=TsvFileSortValueOrder.INVALID_EMPTY_VALID,
            reverse=True,
        ),
    ]

    file_path = pathlib.Path("tests/test-data/test-data-01/s_sample_with_types.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 100

    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Date]",
            column_sort_type=SortType.DATETIME,
            default_datetime_pattern="%d/%m/%Y",
            value_order=TsvFileSortValueOrder.EMPTY_INVALID_VALID,
            reverse=False,
        ),
    ]
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 100


def test_with_multi_column_sort_option_01():
    sort_options = [
        TsvFileSortOption(
            column_name="Characteristics[Organism]", reverse=False, case_sensitive=False
        ),
        TsvFileSortOption(
            column_name="Factor Value[Replicate]",
            reverse=False,
            column_sort_type=SortType.INTEGER,
            value_order=TsvFileSortValueOrder.INVALID_EMPTY_VALID,
        ),
        TsvFileSortOption(
            column_name="Factor Value[Population ID]",
            column_sort_type=SortType.FLOAT,
            value_order=TsvFileSortValueOrder.VALID_EMPTY_INVALID,
            reverse=False,
        ),
        TsvFileSortOption(
            column_name="Factor Value[Date]",
            column_sort_type=SortType.DATETIME,
            default_datetime_pattern="%d/%m/%Y",
            value_order=TsvFileSortValueOrder.VALID_INVALID_EMPTY,
            reverse=True,
        ),
    ]

    file_path = pathlib.Path("tests/test-data/test-data-01/s_sample_with_types.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 100


def test_with_multi_column_sort_filter_option_02():
    filter_options = [
        TsvFileFilterOption(
            search_columns=[],
            search_ignore_columns=["Factor Value[Replicate]"],
            operation=FilterOperation.STARTSWITH,
            parameter="Invalid",
            case_sensitive=False,
            negate_result=False,
        ),
        TsvFileFilterOption(
            search_columns=["Characteristics[Organism]"],
            operation=FilterOperation.EQUAL,
            parameter="blank",
            case_sensitive=False,
            negate_result=True,
        ),
    ]

    sort_options = [
        TsvFileSortOption(
            column_name="Characteristics[Organism]", reverse=False, case_sensitive=False
        )
    ]

    file_path = pathlib.Path("tests/test-data/test-data-01/s_sample_with_types.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 7

    filter_options = [
        TsvFileFilterOption(
            search_columns=[],
            operation=FilterOperation.STARTSWITH,
            parameter="invalid",
            case_sensitive=False,
            negate_result=False,
        ),
        TsvFileFilterOption(
            search_columns=["Characteristics[Organism]"],
            operation=FilterOperation.EQUAL,
            parameter="blank",
            case_sensitive=False,
            negate_result=True,
        ),
    ]

    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 10
