# metabolights-utils






<a href="https://isa-specs.readthedocs.io/en/latest/isatab.html" target="_blank">
    <img src="https://img.shields.io/badge/ISA--Tab-v1.0-dark_blue" alt="ISA-Tab version">
</a>
<a href="https://github.com/EBI-Metabolights/MtblsWS-Py" target="_blank">
    <img src="https://img.shields.io/badge/MetaboLights-v2.0.0-dark_blue" alt="ISA-Tab version">
</a>


![Python](https://img.shields.io/badge/Python-3.8%7C3.9-dark_blue)
![Coverage](https://img.shields.io/badge/Coverge-81%-dark_blue)

MetaboLigts-utils project contains lightweight data models and utilities to read and validate ISA files.

Read an Investigation File
```python 
    import pathlib

    from metabolights_utils.isatab.helper.investigation_file_helper import InvestigationFileHelper
    from metabolights_utils.isatab.investigation_file_reader import InvestigationFileReaderResult
    from metabolights_utils.isatab.isatab_file_helper import IsaTabFileHelper
    from metabolights_utils.models.isa.investigation_file import Assay, Study


        file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
        helper: InvestigationFileHelper = IsaTabFileHelper.get_investigation_file_reader()
        result: InvestigationFileReaderResult = helper.read(file_path=file_path)
        study: Study = result.investigation.studies[0]
        for item in study.studyAssays:
            assay: Assay = item
            assay_file_name = assay.fileName
            print(assay_file_name)
```




Read an assay file with filter and sort options
```python

    from metabolights_utils.isatab.isa_table_file_reader import (
        IsaTableFileReader,
        IsaTableFileReaderResult,
    )
    from metabolights_utils.isatab.isatab_file_helper import IsaTabFileHelper
    from metabolights_utils.models.isa.parser.filter import (
        FilterOperation,
        TsvFileFilterOption,
    )
    from metabolights_utils.models.isa.parser.sort import (
        SortType,
        TsvFileSortOption,
    )


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

    file_path = pathlib.Path("tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt")

    helper: IsaTableFileReader = IsaTabFileHelper.get_assay_file_reader()

    result: IsaTableFileReaderResult = helper.get_page(
        page=1,
        results_per_page=50,
        file_path=file_path,
        sort_options=sort_options,
        filter_options=filter_options,
        selected_columns=selected_columns,
    )
```