import pathlib

from metabolights_utils.isatab import Reader
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.tsv.filter import FilterOperation, TsvFileFilterOption
from metabolights_utils.tsv.sort import SortType, TsvFileSortOption


def test_with_filter_and_sort_option_01():
    # Sample Name value does not start with 'control'  and
    # Parameter Value[Chromatography Instrument] value is 'Thermo Scientific TRACE GC Ultra'.
    # Both filters are applied in case insesitive mode.
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

    # sort by Sample Name and 'Parameter Value[Chromatography Instrument]'
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

    # Result pages will contain second 111 rows (page 2) after filter and sort operations.
    # Selected columns are not set. Result will contain all columns.
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

    selected_columns = [
        "Sample Name",
        "Parameter Value[Column model]",
        "Parameter Value[Column type]",
    ]

    # Result pages will contain third 50 rows (page 3) after filter and sort operations.
    # 3 columns are selected. Result will contain 3 selected columns.
    result: IsaTableFileReaderResult = helper.get_page(
        page=3,
        results_per_page=50,
        file_buffer_or_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=selected_columns,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50

    # First filter applies regex epression math on Sample Name column in case insensitive mode
    # Second filter is exact match on Parameter Value[Chromatography Instrument]
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

    selected_columns = [
        "Sample Name",
        "Parameter Value[Column model]",
        "Parameter Value[Column type]",
        "Parameter Value[Autosampler model]",
    ]

    # Result pages will be 111 and read 2. page after filter operations (No sort options).
    # Selected columns are set. Result will contain 6 columns.
    # 4 selected columns + Term Source REF and Term Accession Number columns of Parameter Value[Autosampler model].
    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=111,
        file_buffer_or_path=file_path,
        selected_columns=selected_columns,
        filter_options=filter_options,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 60
