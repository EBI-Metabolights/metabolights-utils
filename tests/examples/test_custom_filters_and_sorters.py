import pathlib
from enum import Enum

from metabolights_utils.isatab import Reader
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.tsv.filter import (
    FilterDataType,
    FilterOperation,
    TsvFileFilterOption,
)
from metabolights_utils.tsv.sort import (
    SortType,
    TsvFileSortOption,
    TsvFileSortValueOrder,
)


def test_with_custom_filter_between_equal_01():
    filter_options = [
        TsvFileFilterOption(
            search_columns=["Factor Value[Population ID]"],
            operation=FilterOperation.CUSTOM,
            custom_filter_name="between-equal",
            data_type=FilterDataType.FLOAT,
            custom_filter_arguments={"min": 4.3, "max": 5.5},
        )
    ]

    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Population ID]",
            reverse=False,
            column_sort_type=SortType.FLOAT,
            value_order=TsvFileSortValueOrder.INVALID_EMPTY_VALID,
        ),
    ]

    file_path = pathlib.Path("tests/test-data/test-data-01/s_sample_with_types.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        filter_options=filter_options,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 12


def test_with_custom_filter_valid_number_01():
    filter_options = [
        TsvFileFilterOption(
            search_columns=["Factor Value[Population ID]"],
            operation=FilterOperation.CUSTOM,
            custom_filter_name="valid-number",
            negate_result=True,
        )
    ]

    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Population ID]",
            reverse=False,
            column_sort_type=SortType.STRING,
        ),
    ]

    file_path = pathlib.Path("tests/test-data/test-data-01/s_sample_with_types.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        filter_options=filter_options,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 11


class ReplicateTestEnum(Enum):
    VAL1 = 1
    VAL2 = 2
    VAL3 = 3
    VAL4 = 4
    VAL5 = 5
    VAL6 = 6


def test_with_custom_sorter_01():
    filter_options = [
        TsvFileFilterOption(
            search_columns=["Factor Value[Replicate]"],
            operation=FilterOperation.CUSTOM,
            custom_filter_name="enum-contains",
            parameter="Week",
            case_sensitive=False,
            custom_filter_arguments={
                "enum-class": ReplicateTestEnum,
                "enum-value-map": {
                    1: "Week",
                    2: "Day",
                    3: "Day1Week",
                    4: "Day2",
                    5: "lastweek1",
                    6: "Day 5",
                },
            },
        )
    ]

    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Replicate]",
            reverse=False,
            column_sort_type=SortType.CUSTOM,
            custom_sorter_name="enum-sorter",
            value_order=TsvFileSortValueOrder.VALID_EMPTY_INVALID,
            custom_sorter_arguments={
                "enum-class": ReplicateTestEnum,
                "enum-value-map": {
                    1: "Day 6",
                    2: "Day 3",
                    3: "Day 4",
                    4: "Day 2",
                    5: "Day 1",
                    6: "Day 5",
                },
            },
        ),
    ]

    file_path = pathlib.Path("tests/test-data/test-data-01/s_sample_with_enum.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        filter_options=filter_options,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 6

    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Replicate]",
            reverse=False,
            column_sort_type=SortType.CUSTOM,
            custom_sorter_name="enum-sorter",
            value_order=TsvFileSortValueOrder.INVALID_EMPTY_VALID,
            custom_sorter_arguments={
                "enum-class": "tests.examples.test_custom_filters_and_sorters:ReplicateTestEnum",
                "enum-value-map": {
                    1: "Day 6",
                    2: "Day 3",
                    3: "Day 4",
                    4: "Day 2",
                    5: "Day 1",
                    6: "Day 5",
                },
            },
        ),
    ]

    file_path = pathlib.Path("tests/test-data/test-data-01/s_sample_with_enum.txt")
    helper: IsaTableFileReader = Reader.get_sample_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        filter_options=None,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 45
