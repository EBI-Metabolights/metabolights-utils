<a href="https://isa-specs.readthedocs.io/en/latest/isatab.html" target="_blank">
    <img src="https://img.shields.io/badge/ISA--Tab-v1.0-dark_blue" alt="ISA-Tab version">
</a>
<a href="https://github.com/EBI-Metabolights/MtblsWS-Py" target="_blank">
    <img src="https://img.shields.io/badge/MetaboLights-v2.0.0-dark_blue" alt="ISA-Tab version">
</a>


![Python](https://img.shields.io/badge/Python-3.8%7C3.9-dark_blue)
![Coverage](https://img.shields.io/badge/Coverage-80%25-dark_blue)

# MetaboLights Utils Library
MetaboLigts-utils is a lightweight library to read and validate ISA files. 

Selected features:
1. Read and update ISA investigation files. Reading investigation files has *no pandas library dependency*.
2. Read tab seperated ISA files (s_*.txt, a_*.txt, m_*.txt) with **pagination support**.
3. Apply **multi-column filters and sort options** before reading ISA table files. 
    * Multiple sort options can be defined for different columns. For example; sort by 'Parameter Value\[Gender\]' as ascending and Parameter Value\[Age\] as descending order. Moreover, columns can be sorted as different data type (if column values are valid for the selected data type). Supported data types are str, int, float and datetime. 
    * There are **10 different filters** (with inverse options). Any filter can be applied to any column. Multiple filters can be defined. 
        - CONTAINS / NOT CONTAINS
        - EQUAL / NOT EQUAL
        - STARTSWITH / NOT STARTSWITH
        - ENDSWITH / NOT ENDSWITH
        - GREATER / NOT GREATER
        - GREATER_EQUAL / NOT GREATER_EQUAL
        - LESS / NOT LESS
        - LESS_EQUAL / NOT LESS_EQUAL
        - REGEX (regex match) / NOT REGEX (not regex match)
        - EMPTY / NOT EMPTY (None or empty)
4. Define and **apply actions** to manuplate ISA table files. Supported operations:
    * ADD_ROW: Insert rows to given index
    * DELETE_ROW: delete selected rows
    * MOVE_ROW: move row to new index
    * ADD_COLUMN: Add new column
    * DELETE_COLUMN: delete selected columns
    * MOVE_COLUMN: move column to new index
    * COPY_ROW: copy row data to other selected rows
    * COPY_COLUMN: copy column data to other selected columns
    * UPDATE_ROW_DATA: update selected rows
    * UPDATE_COLUMN_DATA: selected columns
    * UPDATE_COLUMN_HEADER: update column headers
    * UPDATE_CELL_DATA: update cells given with row and column index

### Investigation file operations

Read and update an investigation file
```python 
import os
import pathlib
import uuid
from ast import List

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights_utils.isatab.writer import InvestigationFileWriter
from metabolights_utils.models.isa.common import OntologyItem
from metabolights_utils.models.isa.investigation_file import Assay, Study


def test_investigation_file_write_01():
    file_path = pathlib.Path("tests/test-data/MTBLS398/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_path=file_path)

    assay: Assay = result.investigation.studies[0].study_assays.assays[0]
    assay.measurement_type = OntologyItem(
        term="test",
        term_source_ref="test source",
        term_accession_number="test accesion",
    )

    tmp_file_name = uuid.uuid4().hex
    tmp_path = pathlib.Path(f"/tmp/test_{tmp_file_name}.txt")
    writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
    writer.write(result.investigation, file_path=tmp_path)

    result: InvestigationFileReaderResult = reader.read(file_path=tmp_path)
    assay_read: Assay = result.investigation.studies[0].study_assays.assays[0]
    assert assay_read.measurement_type.term == "test"
    assert assay_read.measurement_type.term_source_ref == "test source"
    assert assay_read.measurement_type.term_accession_number == "test accesion"
    os.remove(tmp_path)

```

### Pagination support

Read selected assay file (a_*.txt) rows and columns with pagination support. You can use same methods with sample (s_*.txt) and metabolite assignment (m_*.tsv) files.
```python
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
    page_count: int = reader.get_total_pages(file_path=file_path)
    assert page_count == 147

    # get page count with custom page count.
    page_count = reader.get_total_pages(file_path=file_path, results_per_page=50)
    assert page_count == 294

    # get total row count
    total_rows_count = reader.get_total_row_count(file_path=file_path)
    assert total_rows_count == 14670

    # get isa table headers
    result: IsaTableFileReaderResult = reader.get_headers(file_path=file_path)
    assert len(result.parser_report.messages) == 0
    assert "Parameter Value[Column model]" in result.isa_table_file.table.columns

    # get isa table rows. Default offset is 0. Read 88 rows
    result: IsaTableFileReaderResult = reader.get_rows(file_path=file_path, limit=88)
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 88

    # get isa table rows. Read 70 rows from offset 14600
    result: IsaTableFileReaderResult = reader.get_rows(
        file_path=file_path, offset=14600, limit=70
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 70
    assert result.isa_table_file.table.row_offset == 14600

    # get page 2 from isa table. Default page limit is 100. Read 100 items from offset 100
    result: IsaTableFileReaderResult = reader.get_page(page=2, file_path=file_path)
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 100

    # get page 2 from isa table. Read 50 items from offset 50
    result: IsaTableFileReaderResult = reader.get_page(
        page=2, results_per_page=50, file_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50

    # get last from isa table. Read 20 items from offset 14650
    result: IsaTableFileReaderResult = reader.get_page(
        page=294, results_per_page=50, file_path=file_path
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 20

    # get page 2 with selected columns from isa table.
    # read 50 items from offset 50 (page 2)
    # If addition columns are not added to result even if they are not selected.
    result: IsaTableFileReaderResult = reader.get_page(
        page=2,
        results_per_page=50,
        file_path=file_path,
        selected_columns=["Sample Name", "Parameter Value[Autosampler model]"],
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50
    #
    assert len(result.isa_table_file.table.columns) == 4
```

### Multi-column filters and sort options

Users can apply multiple filters and sort operations before retriving ISA table rows.

```python
import pathlib

from metabolights_utils.isatab import Reader
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.models.isa.common import (
    FilterOperation,
    SortType,
    TsvFileFilterOption,
    TsvFileSortOption,
    TsvFileSortValueOrder,
)


def test_with_filter_and_sort_option_01():
    # Sample Name value does not start with 'control'  and
    # Parameter Value[Chromatography Instrument] value is 'Thermo Scientific TRACE GC Ultra'.
    # Both filters are applied in case insesitive mode.
    filter_options = [
        TsvFileFilterOption(
            column_name="Sample Name",
            operation=FilterOperation.STARTSWITH,
            parameter="control",
            case_sensitive=False,
            negate_result=True,
        ),
        TsvFileFilterOption(
            column_name="Parameter Value[Chromatography Instrument]",
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
        file_path=file_path,
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
        file_path=file_path,
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
            column_name="Sample Name",
            operation=FilterOperation.REGEX,
            parameter="^PG[\d]5.*_5$",
            case_sensitive=False,
        ),
        TsvFileFilterOption(
            column_name="Parameter Value[Chromatography Instrument]",
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
        file_path=file_path,
        selected_columns=selected_columns,
        filter_options=filter_options,
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 60

```

### Update ISA table files
Load ISA table page and save after update

```python
import os
import pathlib
import shutil

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.isatab.writer import IsaTableFileWriter


def test_assay_file_read_write():
    path_original = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    file_path = (
        ".test-temp/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    shutil.copy(path_original, file_path)
    helper: IsaTableFileReader = Reader.get_assay_file_reader()

    with open(file_path, "r") as file_buffer:
        # read second page of assa file
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
        assert result.isa_table_file.table.row_count == 50
        assert len(result.isa_table_file.table.columns) == 3
    
    writer: IsaTableFileWriter = Writer.get_assay_file_writer()
    sha256 = "6ea4c731ce35165f83a5d30438cd8753a6afa5fa9a1109893ffc1c213b1da869"
    isa_table = result.isa_table_file.table
    # save same content without any update
    report = writer.save_isa_table(
        file_path=str(file_path), file_sha256_hash=sha256, isa_table=isa_table
    )
    assert report.success

    first_column = result.isa_table_file.table.columns[0]
    result.isa_table_file.table.data[first_column][0] = "Updated Sample Name"
    # save updated content
    report = writer.save_isa_table(
        file_path=str(file_path), file_sha256_hash=sha256, isa_table=isa_table
    )
    assert report.success
    assert report.updated_file_sha256_hash != sha256
    assert not report.message

```

### Apply actions on ISA table files

User can manuplate ISA table files in row, column or cell level.


View **actions and model definition** from [a this file](https://github.com/EBI-Metabolights/metabolights-utils/blob/master/metabolights_utils/tsv/model.py).

View **examples** from [a this file](https://github.com/EBI-Metabolights/metabolights-utils/blob/master/tests/metabolights_utils/isatab/test_isa_table_actions.py).
