import pathlib
import shutil
from enum import Enum

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.isatab.writer import IsaTableFileWriter
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


def test_assay_metadata_file_success_01():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
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
        selected_columns=[
            "Sample Name",
            "Derived Spectral Data File",
            "Metabolite Assignment File",
        ],
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50
    assert len(result.isa_table_file.table.columns) == 3


def test_assay_metadata_file_success_02():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    # with default results_per_page value - 100
    with file_path.open("r", encoding="utf-8") as file_buffer:
        page_count: int = helper.get_total_pages(file_buffer_or_path=file_buffer)
        assert page_count == 2

    with file_path.open("r", encoding="utf-8") as file_buffer:
        page_count = helper.get_total_pages(
            file_buffer_or_path=file_buffer, results_per_page=20
        )
        assert page_count == 7

    with file_path.open("r", encoding="utf-8") as file_buffer:
        total_rows_count = helper.get_total_row_count(file_buffer_or_path=file_buffer)
        assert total_rows_count == 132
    with file_path.open("r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_headers(
            file_buffer_or_path=file_buffer
        )
        assert len(result.parser_report.messages) == 0

    with file_path.open("r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_rows(
            file_buffer_or_path=file_buffer, limit=88
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 88

    with file_path.open("r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_rows(
            file_buffer_or_path=file_buffer,
            offset=100,
            limit=88,
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 32
    with file_path.open("r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer_or_path=file_buffer,
            page=2,
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 32

    with file_path.open("r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer_or_path=file_buffer,
            page=2,
            results_per_page=50,
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 50

    with file_path.open("r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer_or_path=file_buffer,
            page=2,
            results_per_page=50,
            selected_columns=[
                "Sample Name",
                "Derived Spectral Data File",
                "Metabolite Assignment File",
            ],
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 50
        assert len(result.isa_table_file.table.columns) == 3


def test_assay_metadata_file_success_03():
    """
    Test file_path with str type and file_buffer
    """
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    # with default results_per_page value - 100

    with file_path.open("r", encoding="utf-8") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer_or_path=file_buffer,
            page=2,
            results_per_page=50,
            selected_columns=[
                "Sample Name",
                "Derived Spectral Data File",
                "Metabolite Assignment File",
            ],
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 50
        assert len(result.isa_table_file.table.columns) == 3


def test_assay_metadata_file_read_write():
    path_original = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    file_path = pathlib.Path(
        "test-temp/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(path_original, file_path)
        helper: IsaTableFileReader = Reader.get_assay_file_reader()
        # with default results_per_page value - 100

        with file_path.open("r", encoding="utf-8") as file_buffer:
            result: IsaTableFileReaderResult = helper.get_page(
                file_buffer_or_path=file_buffer,
                page=2,
                results_per_page=50,
                selected_columns=[
                    "Sample Name",
                    "Derived Spectral Data File",
                    "Metabolite Assignment File",
                ],
            )
            assert len(result.parser_report.messages) == 0
            assert result.isa_table_file.table.row_count == 50
            assert len(result.isa_table_file.table.columns) == 3

        writer: IsaTableFileWriter = Writer.get_assay_file_writer()
        isa_table = result.isa_table_file.table
        sha256_hash = result.isa_table_file.sha256_hash
        report = writer.save_isa_table(
            file_path=str(file_path), file_sha256_hash=sha256_hash, isa_table=isa_table
        )
        assert report.success

        first_column = result.isa_table_file.table.columns[0]
        result.isa_table_file.table.data[first_column][0] = "Updated Sample Name"
        report = writer.save_isa_table(
            file_path=str(file_path), file_sha256_hash=sha256_hash, isa_table=isa_table
        )
        assert report.success
        assert report.updated_file_sha256_hash != sha256_hash
        assert not report.message
    finally:
        if file_path.exists():
            file_path.unlink(missing_ok=True)


def test_assay_metadata_file_success_04():
    """
    Test file_path input with str type
    """
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    # with default results_per_page value - 100
    result: IsaTableFileReaderResult = helper.get_page(
        file_buffer_or_path=file_path,
        page=2,
        results_per_page=50,
        selected_columns=[
            "Sample Name",
            "Derived Spectral Data File",
            "Metabolite Assignment File",
        ],
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50
    assert len(result.isa_table_file.table.columns) == 3


def test_assay_metadata_file_invalid_input_01():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()

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


def test_with_filter_and_sort_option_01():
    selected_columns = [
        "Sample Name",
        "Protocol REF.2",
        "Parameter Value[Instrument]",
        "Term Source REF.4",
        "Term Accession Number.4",
        "Parameter Value[Sample pH]",
    ]

    filter_options = [
        TsvFileFilterOption(
            search_columns=["Sample Name"],
            operation=FilterOperation.STARTSWITH,
            parameter="ADG19007u_3",
        ),
        TsvFileFilterOption(
            search_columns=["Parameter Value[Sample pH]"],
            operation=FilterOperation.GREATER,
            parameter=1.0,
        ),
    ]

    sort_options = [
        TsvFileSortOption(column_name="Sample Name", reverse=True),
        TsvFileSortOption(
            column_name="Parameter Value[Sample pH]",
            column_sort_type=SortType.FLOAT,
            reverse=False,
        ),
    ]
    file_path = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=50,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 14
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=50,
        file_buffer_or_path=file_path,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50


class ExampleValueEnum(Enum):
    VAL1 = 1
    VAL2 = 2
    VAL3 = 3
    VAL4 = 4
    VAL5 = 5
    VAL6 = 6


def test_with_filter_and_sort_option_datetime_enum_01():
    selected_columns = [
        "Sample Name",
        "Parameter Value[Float Measurement]",
        "Parameter Value[Int Measurement]",
        "Parameter Value[Enum Value 1]",
        "Parameter Value[Enum Value 2]",
        "Parameter Value[Date Value 1]",
        "Parameter Value[Date Value 2]",
        "Parameter Value[Random Value 1]",
        "Parameter Value[String Value 1]",
        "Parameter Value[String Value 2]",
    ]

    filter_options = [
        TsvFileFilterOption(
            search_columns=["Parameter Value[Float Measurement]"],
            operation=FilterOperation.EMPTY,
            negate_result=True,
        ),
        TsvFileFilterOption(
            search_columns=["Parameter Value[String Value 1]"],
            operation=FilterOperation.REGEX,
            parameter="^sh[a-z]*$",
        ),
        TsvFileFilterOption(
            search_columns=["Parameter Value[Date Value 1]"],
            operation=FilterOperation.LESS,
            data_type=FilterDataType.DATETIME,
            parameter="01/06/2024",
        ),
    ]

    sort_options = [
        TsvFileSortOption(
            column_name="Parameter Value[Enum Value 1]",
            reverse=False,
            column_sort_type=SortType.CUSTOM,
            custom_sorter_name="enum-sorter",
            value_order=TsvFileSortValueOrder.VALID_EMPTY_INVALID,
            custom_sorter_arguments={
                "enum-class": "tests.metabolights_utils.isatab.test_assay_file:ExampleValueEnum",
                "enum-value-map": {
                    1: "Day 6",
                    2: "Day 1",
                    3: "Day 4",
                    4: "Day 3",
                    5: "Day 2",
                    6: "Day 5",
                },
            },
            case_sensitive=False,
        ),
        TsvFileSortOption(
            column_name="Parameter Value[Date Value 1]",
            column_sort_type=SortType.DATETIME,
            reverse=False,
        ),
    ]
    file_path = pathlib.Path(
        "tests/test-data/test-data-02/a_test_assay_file_with_types.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 81


def test_with_filter_and_sort_option_datetime_enum_02():
    selected_columns = [
        "Sample Name",
        "Parameter Value[Float Measurement]",
        "Parameter Value[Int Measurement]",
        "Parameter Value[Enum Value 1]",
        "Parameter Value[Enum Value 2]",
        "Parameter Value[Date Value 1]",
        "Parameter Value[Date Value 2]",
        "Parameter Value[Random Value 1]",
        "Parameter Value[String Value 1]",
        "Parameter Value[String Value 2]",
    ]

    filter_options = [
        TsvFileFilterOption(
            search_columns=["Parameter Value[Int Measurement]"],
            operation=FilterOperation.GREATER_EQUAL,
            data_type=FilterDataType.INTEGER,
            parameter=50,
        ),
        TsvFileFilterOption(
            search_columns=["Parameter Value[Int Measurement]"],
            operation=FilterOperation.LESS_EQUAL,
            data_type=FilterDataType.INTEGER,
            parameter=80,
        ),
    ]

    sort_options = [
        TsvFileSortOption(
            column_name="Parameter Value[Enum Value 1]",
            reverse=False,
            column_sort_type=SortType.CUSTOM,
            custom_sorter_name="enum-sorter",
            value_order=TsvFileSortValueOrder.VALID_EMPTY_INVALID,
            custom_sorter_arguments={
                "enum-class": "tests.metabolights_utils.isatab.test_assay_file:ExampleValueEnum",
                "enum-value-map": {
                    1: "Day 6",
                    2: "Day 1",
                    3: "Day 4",
                    4: "Day 3",
                    5: "Day 2",
                    6: "Day 5",
                },
            },
        ),
        TsvFileSortOption(
            column_name="Parameter Value[Date Value 1]",
            column_sort_type=SortType.DATETIME,
            reverse=True,
        ),
    ]
    file_path = pathlib.Path(
        "tests/test-data/test-data-02/a_test_assay_file_with_types.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=50,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.filtered_total_row_count == 4585


def test_with_filter_and_sort_option_datetime_enum_3():
    selected_columns = [
        "Sample Name",
        "Parameter Value[Float Measurement]",
        "Parameter Value[Int Measurement]",
        "Parameter Value[Enum Value 1]",
        "Parameter Value[Enum Value 2]",
        "Parameter Value[Date Value 1]",
        "Parameter Value[Date Value 2]",
        "Parameter Value[Random Value 1]",
        "Parameter Value[String Value 1]",
        "Parameter Value[String Value 2]",
    ]

    filter_options = [
        TsvFileFilterOption(
            search_columns=["Parameter Value[Float Measurement]"],
            operation=FilterOperation.CUSTOM,
            custom_filter_name="valid-number",
            parameter=1.0,
        ),
        TsvFileFilterOption(
            search_columns=["Parameter Value[Date Value 2]"],
            operation=FilterOperation.CUSTOM,
            custom_filter_name="valid-datetime",
            default_datetime_pattern="%d/%m/%Y",
        ),
        TsvFileFilterOption(
            search_columns=["Parameter Value[Int Measurement]"],
            operation=FilterOperation.CUSTOM,
            custom_filter_name="between-equal",
            negate_result=False,
            custom_filter_arguments={"min": 30, "max": 105},
        ),
        TsvFileFilterOption(
            search_columns=["Parameter Value[Enum Value 1]"],
            operation=FilterOperation.CUSTOM,
            custom_filter_name="enum-contains",
            parameter="week",
            case_sensitive=False,
            custom_filter_arguments={
                "enum-class": "tests.metabolights_utils.isatab.test_assay_file:ExampleValueEnum",
                "enum-value-map": {
                    1: "Year",
                    2: "Last week",
                    3: "Day 4",
                    4: "Month",
                    5: "Weeek",
                    6: "Weekend",
                },
            },
        ),
    ]

    sort_options = [
        TsvFileSortOption(
            column_name="Parameter Value[Enum Value 1]",
            reverse=False,
            column_sort_type=SortType.CUSTOM,
            custom_sorter_name="enum-sorter",
            value_order=TsvFileSortValueOrder.VALID_EMPTY_INVALID,
            custom_sorter_arguments={
                "enum-class": "tests.metabolights_utils.isatab.test_assay_file:ExampleValueEnum",
                "enum-value-map": {
                    1: "Day 6",
                    2: "Day 1",
                    3: "Day 4",
                    4: "Day 3",
                    5: "Day 2",
                    6: "Day 5",
                },
            },
        ),
        TsvFileSortOption(
            column_name="Parameter Value[Date Value 1]",
            column_sort_type=SortType.DATETIME,
            reverse=True,
        ),
    ]
    file_path = pathlib.Path(
        "tests/test-data/test-data-02/a_test_assay_file_with_types.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=50,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.filtered_total_row_count == 3733
