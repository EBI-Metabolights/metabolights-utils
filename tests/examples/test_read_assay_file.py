import pathlib

from metabolights_utils.isatab import Reader
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)


def test_assay_file_success_01():
    file_path = pathlib.Path(
        "tests/test-data/MTBLS373/a_MTBLS373_sevinaskascreen_metabolite_profiling_mass_spectrometry.txt"
    )
    reader: IsaTableFileReader = Reader.get_assay_file_reader()

    # get page count. Default results per page is 100
    page_count: int = reader.get_total_pages(file_buffer_or_path=file_path)
    assert page_count == 147

    # get page count with custom page count.
    page_count = reader.get_total_pages(
        file_buffer_or_path=file_path, results_per_page=50
    )
    assert page_count == 294

    # get total row count
    total_rows_count = reader.get_total_row_count(file_buffer_or_path=file_path)
    assert total_rows_count == 14670

    # get isa table headers
    result: IsaTableFileReaderResult = reader.get_headers(file_buffer_or_path=file_path)
    assert len(result.parser_report.messages) == 0
    assert "Parameter Value[Column model]" in result.isa_table_file.table.columns

    # get isa table rows. Default offset is 0. Read 88 rows
    result: IsaTableFileReaderResult = reader.get_rows(
        file_buffer_or_path=file_path, limit=88
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 88

    # get isa table rows. Read 70 rows from offset 14600
    result: IsaTableFileReaderResult = reader.get_rows(
        file_buffer_or_path=file_path, offset=14600, limit=70
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 70
    assert result.isa_table_file.table.row_offset == 14600

    # get page 2 from isa table. Default page limit is 100. Read 100 items from offset 100
    result: IsaTableFileReaderResult = reader.get_page(
        page=2, file_buffer_or_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 100

    # get page 2 from isa table. Read 50 items from offset 50
    result: IsaTableFileReaderResult = reader.get_page(
        page=2, results_per_page=50, file_buffer_or_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50

    # get last from isa table. Read 20 items from offset 14650
    result: IsaTableFileReaderResult = reader.get_page(
        page=294, results_per_page=50, file_buffer_or_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 20

    # get page 2 with selected columns from isa table.
    # read 50 items from offset 50 (page 2)
    # Addition columns will be in result even if they are not selected.
    # Parameter Value[Autosampler model] is ontology column,
    # so Term Source REF and Term Accesion Number columns of it will be added.
    result: IsaTableFileReaderResult = reader.get_page(
        page=2,
        results_per_page=50,
        file_buffer_or_path=file_path,
        selected_columns=["Sample Name", "Parameter Value[Autosampler model]"],
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50
    #
    assert len(result.isa_table_file.table.columns) == 4
