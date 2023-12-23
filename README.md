



# <img src="https://www.ebi.ac.uk/metabolights/img/MetaboLightsLogo.png" width="30" height="30" alt="Metabolights"> MetaboLights Utils Library

<a href="https://isa-specs.readthedocs.io/en/latest/isatab.html" target="_blank">
    <img src="https://img.shields.io/badge/ISA--Tab-v1.0-blue" alt="ISA-Tab version">
</a>
<a href="https://github.com/EBI-Metabolights/MtblsWS-Py" target="_blank">
    <img src="https://img.shields.io/badge/MetaboLights-v2.0.0-blue" alt="ISA-Tab version">
</a>
<a href="https://github.com/EBI-Metabolights/metabolights-utils/blob/master/LICENCE" target="_blank">
    <img src="https://img.shields.io/badge/Licence-Apache%20v2.0-blue" alt="Licence">
</a>

![Python](https://img.shields.io/badge/Python-3.8%7C3.9-dark_blue)
![Coverage](https://img.shields.io/badge/Coverage-85%25-dark_blue)

---

#### **MetaboLigts-utils** is a *lightweight library* to read and update ISA files, download MetaboLights studies.
---
### Selected Features
---

* **Read and update ISA files** with minimum pyhton package dependency.
* Read ISA table files (s_*.txt, a_*.txt, m_*.txt) with **Pagination support**.
* **Multi-column filters and sort options** on ISA table files.
* Define **custom filters and sorters**
* **Apply actions** on ISA table files to manuplate them.
* **Json serializable** models with [pydantic](https://github.com/pydantic/pydantic) library.


### Installation
---
The following command installs metabolights-utils from the Python Package Index. You will need a working installation of Python 3.8+ and pip3.

```shell
pip3 install -U metabolights-utils
```


### Read and update Investigation files
---
Read and update an investigation file. Results are json serializable, so you can use them with REST APIs.  

```python 
import os
import pathlib
import uuid
from typing import List

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.reader import InvestigationFileReader, InvestigationFileReaderResult
from metabolights_utils.isatab.writer import InvestigationFileWriter
from metabolights_utils.models.isa.common import OntologyItem
from metabolights_utils.models.isa.investigation_file import Assay, Study


def test_investigation_file_write_01():
    file_path = pathlib.Path("tests/test-data/MTBLS398/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)

    assay: Assay = result.investigation.studies[0].study_assays.assays[0]
    assay.measurement_type = OntologyItem(
        term="test",
        term_source_ref="test source",
        term_accession_number="test accesion",
    )

    tmp_file_name = uuid.uuid4().hex
    tmp_path = pathlib.Path(f"/tmp/test_{tmp_file_name}.txt")
    writer: InvestigationFileWriter = Writer.get_investigation_file_writer()
    writer.write(result.investigation, file_buffer_or_path=tmp_path)

    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=tmp_path)
    assay_read: Assay = result.investigation.studies[0].study_assays.assays[0]
    assert assay_read.measurement_type.term == "test"
    assert assay_read.measurement_type.term_source_ref == "test source"
    assert assay_read.measurement_type.term_accession_number == "test accesion"
    os.remove(tmp_path)

```

### Read and Update ISA Table Files with Pagination Support
---
* Select page size (number of rows in a page) and read results with the selected page size.
* Define custom row offset and read only selected rows. Actual row indices in a result may be unordered after filter and sort operations. 
* Read the selected columns you defined. If a selected column has additional columns (Term Source REF, etc) and these columns are not defined by user, they will also be in the result. Column names may be different than header if there are multiple columns with same header. 
* If columns are not selected, all table columns will be returned in result. If columns are selected, result will contain only these columns in selected order.

---
#### Example 1: Read ISA table file
---

Read selected assay file (a_*.txt) rows and columns with pagination support. You can use same methods with sample (s_*.txt) and metabolite assignment (m_*.tsv) files.
```python
import pathlib

from metabolights_utils.isatab import Reader
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult
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
    page_count = reader.get_total_pages(file_buffer_or_path=file_path, results_per_page=50)
    assert page_count == 294

    # get total row count
    total_rows_count = reader.get_total_row_count(file_buffer_or_path=file_path)
    assert total_rows_count == 14670

    # get isa table headers
    result: IsaTableFileReaderResult = reader.get_headers(file_buffer_or_path=file_path)
    assert len(result.parser_report.messages) == 0
    assert "Parameter Value[Column model]" in result.isa_table_file.table.columns

    # get isa table rows. Default offset is 0. Read 88 rows
    result: IsaTableFileReaderResult = reader.get_rows(file_buffer_or_path=file_path, limit=88)
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
    result: IsaTableFileReaderResult = reader.get_page(page=2, file_buffer_or_path=file_path)
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
    # Parameter Value[Autosampler model] is ontology column. So 2 new columns will be added to result.
    result: IsaTableFileReaderResult = reader.get_page(
        page=2,
        results_per_page=50,
        file_buffer_or_path=file_path,
        selected_columns=["Sample Name", "Parameter Value[Autosampler model]"],
    )
    assert len(result.parser_report.messages) == 0
    assert result.isa_table_file.table.row_count == 50
    assert len(result.isa_table_file.table.columns) == 4
```


#### Example 2: Update ISA table file
---

Load ISA table page and save after update table content

```python
import os
import pathlib
import shutil

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult
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

    with open(file_path, "r", encoding="utf-8") as file_buffer:
        # read second page of assa file
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer_or_path=file_buffer,
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
    isa_table = result.isa_table_file.table

    sha256_hash = result.isa_table_file.sha256_hash
    # save same content without any update
    report = writer.save_isa_table(
        file_path=str(file_path), file_sha256_hash=sha256_hash, isa_table=isa_table
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

### Multi-column filters and sort options
---
* Case sensitive or case insensitive multi-column sort is supported.
    - Multi-column sorts can be defined with combination of ascending and descending orders. For example; You can sort 'Parameter Value\[Gender\]' by ascending and Parameter Value\[Age\] by descending order. 
    - Columns can be sorted as different data type. Supported sort data types are: str, int, float and datetime. datetime pattern can be defined.
    - Sort orders for invalid and empty values can also be defined. For example, If it is defined as VALID_EMPTY_INVALID, invalid values will be at the end. Empty values will follow valid values. This value order option is applicable for only int, datetime and float data types. All sort placement combinations are poossible for EMPTY, INVALID, VALID values.
    - You can define your custom sorters. A custom "enum-sorter" sorter has been already implemented. It sorts enums with given string values.

* There are **10 different filters** (plus (NOT) options of them). Any filter can be applied to any column. Multiple filters can be defined. 
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
* You can define multiple filters. If one filter rejects row, row will not be selected (AND operation).
* You can define one or more columns for a filter. If there are multiple columns for a filter. If any column matches, the filter selects the row (OR operation).
* If you do not select any column for a filter, the filter will evaluate all columns. If filter matches with any column, it will select the row. Moreover, you can define some column names to skip them while filter is evaluating a row. 

* You can define your custom filters. Some custom filters have been already implemented.
    - "between-equal": Returns row if value between given min and max. Min and max inputs can be datetime, str, int or float.
    - "valid-datetime" Return row if value is valid datetime with given pattern. Default pattern is DD/MM/YYYY.
    - "valid-number": Return row if value is valid int or float.
    - "enum-contains": Gets a map to define a text for each enum value. Returns row if input parameter is in the enum text map. Enum data typese can be any allowed type (str, int, etc.).
        + Example: Enum values are 1, 2, 3, 4 (You store status values as in on database). Enum values are mapped to 1: "In Review", 2: "Published", 3: "In Curation", 4: "Public". If parameter is "Pub", all rows contain enum value 2 or 4 will be returned.

#### Example
Users can apply multiple filters and sort operations before retriving ISA table rows.

```python
import pathlib

from metabolights_utils.isatab import Reader
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult
)
from metabolights_utils.models.isa.common import (
    FilterOperation,
    SortType,
    TsvFileFilterOption,
    TsvFileSortOption,
    TsvFileSortValueOrder)


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
            parameter="^PG[\d]5.*_5$",
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

```

### Update ISA table files with actions

User can manuplate ISA table files in row, column or cell level with actions. Supported actions:
* ADD_ROW: Insert rows to given indices
* DELETE_ROW: delete selected rows
* MOVE_ROW: move row to new index
* ADD_COLUMN: Add new columns
* DELETE_COLUMN: delete selected columns
* MOVE_COLUMN: move column to new index
* COPY_ROW: copy row data to other selected rows
* COPY_COLUMN: copy column data to other selected columns
* UPDATE_ROW_DATA: update selected row values
* UPDATE_COLUMN_DATA: update selected column values
* UPDATE_COLUMN_HEADER: update column headers
* UPDATE_CELL_DATA: update cells given with row and column index


View **model and action definitions** on [this file](https://github.com/EBI-Metabolights/metabolights-utils/blob/master/metabolights_utils/tsv/model.py).

View **examples** on [this file](https://github.com/EBI-Metabolights/metabolights-utils/blob/master/tests/metabolights_utils/isatab/test_isa_table_actions.py).
