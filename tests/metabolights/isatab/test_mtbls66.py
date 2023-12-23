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


def test_with_sort_option_01():
    sort_options = [
        TsvFileSortOption(
            column_name="Sample Name",
            reverse=False,
            case_sensitive=False,
        ),
        TsvFileSortOption(
            column_name="MS Assay Name",
            column_sort_type=SortType.STRING,
            case_sensitive=False,
            reverse=True,
        ),
    ]
    file_path = pathlib.Path(
        "tests/test-data/MTBLS66/a_MTBLS66_GC_metabolite_profiling_mass_spectrometry.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=43,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 17


def test_with_sort_and_filter_option_02():
    sort_options = [
        TsvFileSortOption(
            column_name="Factor Value[Replicate]",
            column_sort_type=SortType.INTEGER,
            case_sensitive=False,
            value_order=TsvFileSortValueOrder.VALID_INVALID_EMPTY,
            reverse=True,
        ),
        TsvFileSortOption(
            column_name="Factor Value[Country of origin]",
            column_sort_type=SortType.STRING,
            case_sensitive=False,
            value_order=TsvFileSortValueOrder.VALID_INVALID_EMPTY,
            reverse=False,
        ),
        TsvFileSortOption(
            column_name="Factor Value[MFFGC accession no]",
            reverse=False,
            column_sort_type=SortType.INTEGER,
            value_order=TsvFileSortValueOrder.EMPTY_INVALID_VALID,
        ),
    ]
    filter_options = [
        TsvFileFilterOption(
            search_columns=["Sample Name"],
            operation=FilterOperation.STARTSWITH,
            parameter="control",
            case_sensitive=False,
            negate_result=True,
        ),
        TsvFileFilterOption(
            search_columns=["Sample Name"],
            operation=FilterOperation.STARTSWITH,
            parameter="blank",
            case_sensitive=False,
            negate_result=True,
        ),
    ]
    file_path = pathlib.Path("tests/test-data/MTBLS66/s_MTBLS66.txt")
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=70,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
        filter_options=filter_options,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 100
    result: IsaTableFileReaderResult = helper.get_page(
        page=82,
        results_per_page=100,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 67


def test_with_filter_and_sort_option_01():
    filter_options = [
        TsvFileFilterOption(
            search_columns=["Sample Name"],
            operation=FilterOperation.STARTSWITH,
            parameter="control",
            case_sensitive=False,
            negate_result=True,
        ),
        TsvFileFilterOption(
            search_columns=["Parameter Value[Chromatography Instrument]"],
            operation=FilterOperation.EQUAL,
            parameter="Thermo Scientific TRACE GC Ultra",
            case_sensitive=False,
        ),
    ]

    sort_options = [
        TsvFileSortOption(column_name="Sample Name", reverse=False),
        TsvFileSortOption(
            column_name="Parameter Value[Chromatography Instrument]",
            column_sort_type=SortType.STRING,
            reverse=True,
        ),
    ]
    file_path = pathlib.Path(
        "tests/test-data/MTBLS66/a_MTBLS66_GC_metabolite_profiling_mass_spectrometry.txt"
    )
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    result: IsaTableFileReaderResult = helper.get_page(
        page=2,
        results_per_page=111,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=None,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 111

    filter_options = [
        TsvFileFilterOption(
            search_columns=["Sample Name"],
            operation=FilterOperation.REGEX,
            parameter=r"^PG[\d]5.*_5$",
            case_sensitive=False,
        ),
        TsvFileFilterOption(
            search_columns=["Parameter Value[Chromatography Instrument]"],
            operation=FilterOperation.EQUAL,
            parameter="Thermo Scientific TRACE GC Ultra",
            case_sensitive=False,
        ),
    ]

    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=111,
        file_buffer_or_path=file_path,
        selected_columns=None,
        filter_options=filter_options,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 60
