import re
from functools import partial
from io import IOBase
from pathlib import Path
from typing import Callable, List, Tuple, Union

from metabolights_utils.isatab.default.parser.common import (
    SelectedTsvFileContent,
    TsvFileFilterOption,
    read_table_file,
)
from metabolights_utils.models.isa.common import IsaTableColumn, IsaTableFile
from metabolights_utils.models.isa.enums import (
    ColumnsStructure,
    IsaTableAdditionalColumn,
)
from metabolights_utils.models.parser.common import ParserMessage
from metabolights_utils.models.parser.enums import ParserMessageType
from metabolights_utils.tsv.sort import TsvFileSortOption
from metabolights_utils.utils.hash_utils import MetabolightsHashUtils as HashUtils


def fix_isa_table_file(
    file_path: str,
    messages: List[ParserMessage],
    read_encoding: str,
    write_encoding: str,
    fix_empty_rows: bool = True,
    fix_new_lines_in_cells: bool = True,
    max_iteration_to_fix_new_lines_in_cells: int = 5,
):
    if not fix_new_lines_in_cells and not fix_empty_rows:
        return
    file = Path(file_path)
    basename = file.name
    with file.open("r", encoding=read_encoding) as f:
        file_content = f.read()
        find_empty_lines = None
        find_new_lines_in_cells = None
        if fix_empty_rows:
            find_empty_lines = re.findall(r"[\r\n][\r\n]+", file_content)
            if find_empty_lines:
                messages.append(
                    ParserMessage(
                        type=ParserMessageType.WARNING,
                        short=f"Removed empty lines in {basename}.",
                        detail=f"Removed empty lines in {basename}",
                    )
                )
                file_content = re.sub(r"[\r\n][\r\n]+", r"\n", file_content)
        if fix_new_lines_in_cells:
            results = []

            def replace(x: re.Match):
                groups = x.groups()
                input_val = x.group()
                val = re.sub(r"\s", " ", groups[1].strip())

                result = groups[0] + val + groups[0] + groups[2]
                if result != input_val:
                    results.append((groups[1], val))
                return result

            pattern = r'(")([^"]*)\1(\t|\r|\n|$)'
            new_file_content = re.sub(pattern, replace, file_content)
            if results:
                printed_result = results if len(results) < 20 else results[:20]
                printed_result = [
                    (re.sub("\r\t\n", "{ unexpected char }", x[0]), x[1])
                    for x in printed_result
                ]
                messages.append(
                    ParserMessage(
                        type=ParserMessageType.WARNING,
                        short=f"Removed new line characters and unexpected whitespaces in {basename} file table cells.",
                        detail=f"Removed : {str(printed_result)}",
                    )
                )
                file_content = new_file_content

        if find_empty_lines or find_new_lines_in_cells:
            with file.open("w", encoding=write_encoding) as f:
                f.write(file_content)


def parse_isa_file_content(
    parser: Callable,
    file_path: str,
    messages: List[ParserMessage],
    fix_unicode_exceptions: bool = False,
    remove_empty_rows: bool = False,
    remove_new_lines_in_cells: bool = False,
) -> Tuple[IsaTableFile, List[ParserMessage]]:
    file = Path(file_path)
    try:
        if remove_empty_rows:
            fix_isa_table_file(file_path, messages, "utf-8", "utf-8")

        with file.open("r", encoding="utf-8") as f:
            model = parser(f, messages=messages)
            return model, messages
    except UnicodeDecodeError as ex:
        if fix_unicode_exceptions:
            try:
                if remove_empty_rows:
                    fix_isa_table_file(
                        file_path,
                        messages,
                        "latin-1",
                        "latin-1",
                        remove_empty_rows,
                        remove_new_lines_in_cells,
                        max_iteration_to_fix_new_lines_in_cells=5,
                    )
                with file.open("r", encoding="latin-1") as f:
                    model = parser(f, messages=messages)
                    message = ParserMessage(
                        short="File is read with latin-1 encoding",
                        type=ParserMessageType.WARNING,
                    )
                    message.detail = "File is read with latin-1 encoding"
                    messages.append(message)
                    return model, messages
            except Exception as ex:
                message = ParserMessage(
                    short="File read exception", type=ParserMessageType.CRITICAL
                )
                message.detail = f"File parse error: {str(ex)}"
                messages.append(message)
                return None, messages
        else:
            message = ParserMessage(
                short="File read exception", type=ParserMessageType.CRITICAL
            )
            message.detail = f"File parse error: {str(ex)}"
            messages.append(message)
            return None, messages
    except Exception as ex:
        message = ParserMessage(
            short="File read exception", type=ParserMessageType.CRITICAL
        )
        message.detail = f"File parse error: {str(ex)}"
        messages.append(message)
        return None, messages


def parse_isa_table_sheet_from_fs(
    file_path: str,
    expected_patterns: Union[None, List[List[str]]] = None,
    selected_columns: Union[None, List[str]] = None,
    offset: Union[int, None] = None,
    limit: Union[int, None] = None,
    filter_options: List[TsvFileFilterOption] = None,
    sort_options: List[TsvFileSortOption] = None,
    fix_unicode_exceptions: bool = False,
    remove_empty_rows: bool = False,
    remove_new_lines_in_cells: bool = False,
) -> Tuple[IsaTableFile, List[ParserMessage]]:
    file = Path(file_path)
    basename = file.name
    dirname = file.parent.name
    messages: List[ParserMessage] = []
    if not file_path:
        message = ParserMessage(
            short="File path is not valid", type=ParserMessageType.CRITICAL
        )
        message.detail = "File path is not valid"
        messages.append(message)
        return IsaTableFile(), messages

    if not file.exists() or not file.is_file():
        message = ParserMessage(
            short="File does not exist or it is not a file",
            type=ParserMessageType.CRITICAL,
        )
        message.detail = (
            f"File does not exist or is not a file: {basename} in {dirname}"
        )
        messages.append(message)
        return IsaTableFile(), messages

    file_size = file.stat().st_size
    if file_size == 0:
        message = ParserMessage(short="File is empty", type=ParserMessageType.CRITICAL)
        message.detail = f"File is empty: {basename} in {dirname}"
        messages.append(message)
        return IsaTableFile(), messages

    basename = file.name
    parser = partial(
        get_isa_table_file,
        file_name=basename,
        expected_patterns=expected_patterns,
        selected_columns=selected_columns,
        offset=offset,
        limit=limit,
        filter_options=filter_options,
        sort_options=sort_options,
    )
    read_messages: List[ParserMessage] = []
    table, read_messages = parse_isa_file_content(
        parser,
        file_path=file_path,
        messages=read_messages,
        fix_unicode_exceptions=fix_unicode_exceptions,
        remove_empty_rows=remove_empty_rows,
        remove_new_lines_in_cells=remove_new_lines_in_cells,
    )
    isa_table_file: IsaTableFile = table
    if isa_table_file:
        if file.exists():
            isa_table_file.sha256_hash = HashUtils.sha256sum(file_path)
        if isa_table_file.table:
            messages.extend(read_messages)
            messages = [x for x in messages if x.type != ParserMessageType.INFO]
            return isa_table_file, messages

    messages = [x for x in messages if x.type != ParserMessageType.INFO]
    return isa_table_file, messages


def get_isa_table_file(
    file_buffer_or_path: IOBase,
    file_name: str,
    messages: List[ParserMessage],
    expected_patterns: List[List[str]],
    selected_columns: Union[None, List[str]] = None,
    offset: Union[int, None] = None,
    limit: Union[int, None] = None,
    filter_options: List[TsvFileFilterOption] = None,
    sort_options: List[TsvFileSortOption] = None,
) -> IsaTableFile:
    study_table = IsaTableFile()
    if messages is None:
        messages = []
    if not expected_patterns:
        expected_patterns = []
    file_buffer_or_path.seek(0)
    content: SelectedTsvFileContent = read_table_file(
        file_buffer_or_path,
        messages,
        selected_columns,
        offset,
        limit,
        filter_options,
        sort_options,
    )
    if content is None:
        return study_table
    return update_isa_table_file(
        study_table,
        content,
        file_name,
        messages,
        expected_patterns,
    )


def update_isa_table_file(
    study_table: IsaTableFile,
    content: SelectedTsvFileContent,
    file_name: str,
    messages: List[ParserMessage],
    expected_patterns,
):
    columns = [x.column_name for x in content.columns]
    column_indices = {x.column_name: x.column_index for x in content.columns}
    first_column_name = None
    for column_name in columns:
        if not first_column_name:
            first_column_name = column_name
        cleaned_column_name = get_cleaned_header(column_name)

        if not len(cleaned_column_name.strip()) or len(cleaned_column_name) != len(
            cleaned_column_name.strip()
        ):
            message = ParserMessage(type=ParserMessageType.ERROR)
            column_index = column_indices[column_name]
            message.column = str(column_index)
            if len(cleaned_column_name.strip()) > 0:
                message.short = "Column header starts or ends with space"
                message.detail = (
                    f"'{column_name}' header at column {column_index + 1} "
                    + "ends or starts with space."
                )
            else:
                message.short = "Column header is empty"
                message.detail = (
                    f"'{column_name}' header at column {column_index + 1}  is empty."
                )
            messages.append(message)

    headers = get_headers(
        columns, expected_patterns=expected_patterns, messages=messages
    )
    study_table.table.headers = headers
    study_table.table.total_row_count = content.total_rows
    study_table.table.row_offset = content.offset
    study_table.table.row_count = content.limit
    study_table.table.filtered_total_row_count = content.total_filtered_rows
    study_table.table.selected_column_count = content.selected_column_count
    study_table.table.total_column_count = content.total_columns
    study_table.table.filter_options = content.filter_options
    study_table.table.sort_options = content.sort_options

    filtered_data = {}

    for column in content.columns:
        if not study_table.table.row_indices:
            study_table.table.row_indices = [x for x in column.rows]
        filtered_data[column.column_name] = [column.rows[x] for x in column.rows]
    study_table.table.column_indices = [
        column.column_index for column in content.columns
    ]
    # data = df.to_dict(orient="list")
    study_table.table.data = filtered_data
    study_table.table.columns = columns
    # study_table.table.row_count = len(content.columns[0].rows)
    study_table.file_path = file_name
    return study_table


MULTI_COLUMN_TEMPLATES = {
    ColumnsStructure.ONTOLOGY_COLUMN: {
        "column_names": [
            IsaTableAdditionalColumn.TERM_SOURCE_REF,
            IsaTableAdditionalColumn.TERM_ACCSSION_NUMBER,
        ],
        "searchPatterns": [
            r"(Term Source REF)(\.\d+)?",
            r"(Term Accession Number)(\.\d+)?",
        ],
    },
    ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY: {
        "column_names": [
            IsaTableAdditionalColumn.UNIT,
            IsaTableAdditionalColumn.TERM_SOURCE_REF,
            IsaTableAdditionalColumn.TERM_ACCSSION_NUMBER,
        ],
        "searchPatterns": [
            r"(Unit)(\.\d+)?",
            r"(Term Source REF)(\.\d+)?",
            r"(Term Accession Number)(\.\d+)?",
        ],
    },
}

additional_column_templates = [
    MULTI_COLUMN_TEMPLATES[ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY][
        "searchPatterns"
    ],
    MULTI_COLUMN_TEMPLATES[ColumnsStructure.ONTOLOGY_COLUMN]["searchPatterns"],
]

ADDITIONAL_COLUMN_HEADERS = [
    MULTI_COLUMN_TEMPLATES[ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY][
        "column_names"
    ],
    MULTI_COLUMN_TEMPLATES[ColumnsStructure.ONTOLOGY_COLUMN]["column_names"],
]

multiple_columns_additional_header_patterns = MULTI_COLUMN_TEMPLATES[
    ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY
]["searchPatterns"]


samples_file_expected_patterns = [
    [r"^(Source Name)$", ""],
    [r"^Characteristics\[(\w[ -~]*)\](\.\d+)?$", "Characteristics"],
    [r"^(Protocol REF)(\.\d+)?$", "Protocol"],
    [r"^(Sample Name)$", ""],
    [r"^Factor Value\[(\w[ -~]*)\](\.\d+)?$", "Factor Value"],
    [r"^Comment\b\[(\w{1}[ -~]*)\](\.\d+)?$", "Comment"],
]

assay_file_expected_patterns: List[List[str]] = [
    [r"^(Extract Name)$", ""],
    [r"^(Protocol REF)(\.\d+)?$", "Protocol"],
    [r"^(Sample Name)$", ""],
    [r"^[ ]*Parameter[ ]+Value[ ]*\[[ ]*(\w[ -~]*)[ ]*\](\.\d+)?$", "Parameter Value"],
    [r"^Comment\b\[(\w{1}[ -~]*)\](\.\d+)?$", "Comment"],
    [r"^(Labeled Extract Name)$", ""],
    [r"^(Label)$", ""],
]


def get_cleaned_header(column_name: str) -> str:
    cleaned_column_name = column_name
    last_dot = column_name.rfind(".")
    if last_dot > 0:
        left = column_name[:last_dot]
        right = column_name[last_dot:].lstrip(".")
        if right and right.isnumeric():
            cleaned_column_name = left
    return cleaned_column_name


def get_headers(
    columns: List[str],
    expected_patterns: List[List[str]],
    messages: List[ParserMessage],
):
    headers = []
    column_index = 0
    columns_count = len(columns)
    while column_index < columns_count:
        column_name = columns[column_index]
        cleaned_column_name = get_cleaned_header(column_name)
        column_structure, defined_additional_column_headers = define_column_structure(
            column_index, columns
        )

        result = None
        pattern_index = -1
        expected_header: bool = False
        message = ParserMessage(type=ParserMessageType.INFO)
        for i in range(len(expected_patterns)):
            result = re.search(expected_patterns[i][0], column_name)
            if result and result.groups():
                pattern_index = i
                expected_header = result and result.groups()
                break

        column = IsaTableColumn(
            column_index=column_index, column_structure=column_structure
        )
        column.column_name = column_name
        column.column_header = cleaned_column_name
        linked_columns = []

        if column_structure == ColumnsStructure.ADDITIONAL_COLUMN:
            column.column_category = "Additional"
            message.type = ParserMessageType.CRITICAL
            message.short = (
                "Additional column header"
                + f"'{cleaned_column_name}'"
                + "is not linked to a previous header."
            )
        elif column_structure == ColumnsStructure.SINGLE_COLUMN:
            update_as_single_column(
                expected_patterns,
                cleaned_column_name,
                pattern_index,
                expected_header,
                message,
                column,
            )
        elif column_structure == ColumnsStructure.INVALID_MULTI_COLUMN:
            update_as_invalid_column(
                expected_patterns,
                cleaned_column_name,
                pattern_index,
                expected_header,
                message,
                column,
            )
        else:
            column.additional_columns = defined_additional_column_headers
            additional_column_index = column_index

            for item in column.additional_columns:
                additional_column: IsaTableAdditionalColumn = item
                additional_column_index = additional_column_index + 1
                linked_column = IsaTableColumn(
                    column_index=additional_column_index,
                    column_structure=ColumnsStructure.LINKED_COLUMN,
                )
                linked_column.column_header = additional_column.value
                linked_column.column_category = "Linked Column"
                linked_column.column_name = columns[additional_column_index]
                linked_columns.append(linked_column)

            update_as_multi_column(
                expected_patterns,
                cleaned_column_name,
                pattern_index,
                expected_header,
                message,
                column,
            )
            column_index = column_index + len(defined_additional_column_headers)

        headers.append(column)
        if linked_columns:
            headers.extend(linked_columns)

        update_message(messages, column_index, message, column)

        column_index = column_index + 1
    return headers


def update_message(
    messages, column_index, message: ParserMessage, column: IsaTableColumn
):
    if not message.detail:
        column_message = " ".join(
            [
                f"Column {(column.column_index + 1):03}: '{column.column_category}' column",
                f"column name: '{column.column_header}'",
            ]
        )
        message.detail = column_message
    if not message.short:
        message.short = f"'{column.column_category}' column: '{column.column_header}'"
    message.column = str(column_index)
    messages.append(message)


def update_as_multi_column(
    expected_patterns,
    cleaned_column_name,
    pattern_index,
    expected_header,
    message: ParserMessage,
    column: IsaTableColumn,
):
    if expected_header:
        column.column_search_pattern = expected_patterns[pattern_index][0]
        column.column_category = expected_patterns[pattern_index][1]
        column.column_prefix = expected_patterns[pattern_index][1]
    else:
        # column.column_category = "Undefined"
        message.type = ParserMessageType.INFO
        message.short = (
            f"Multi column '{cleaned_column_name}' is not in expected column list."
        )


def update_as_invalid_column(
    expected_patterns,
    cleaned_column_name,
    pattern_index,
    expected_header,
    message: ParserMessage,
    column: IsaTableColumn,
):
    if expected_header:
        column.column_search_pattern = expected_patterns[pattern_index][0]
        column.column_prefix = expected_patterns[pattern_index][1]
        column.column_category = expected_patterns[pattern_index][1]
    else:
        column.column_category = "Invalid"
        message.type = ParserMessageType.CRITICAL
        message.short = (
            f"Multi column '{cleaned_column_name}'"
            + " has invalid or unordered additional headers."
        )


def update_as_single_column(
    expected_patterns,
    cleaned_column_name,
    pattern_index,
    expected_header,
    message: ParserMessage,
    column: IsaTableColumn,
):
    if expected_header:
        column.column_search_pattern = expected_patterns[pattern_index][0]
        column.column_category = expected_patterns[pattern_index][1]
        column.column_prefix = expected_patterns[pattern_index][1]
    else:
        column.column_category = "Undefined"
        message.type = ParserMessageType.INFO
        message.short = (
            f"Single column '{cleaned_column_name}' is not in expected column list."
        )


def define_column_structure(column_index, columns):
    column_is_additional = False
    for additional_column_pattern in multiple_columns_additional_header_patterns:
        if re.match(additional_column_pattern, columns[column_index]):
            column_is_additional = True
            break
    if column_is_additional:
        return ColumnsStructure.ADDITIONAL_COLUMN, []
    selected_additional_columns, additional_columns_count = select_additional_columns(
        column_index, columns
    )
    return evalutate_selected_columns(
        selected_additional_columns, additional_columns_count, column_index, columns
    )


def evalutate_selected_columns(
    selected_additional_columns, additional_columns_count, column_index, columns
):
    columns_count = len(columns)
    if selected_additional_columns:
        if additional_columns_count == 2:
            return ColumnsStructure.ONTOLOGY_COLUMN, selected_additional_columns
        elif additional_columns_count == 3:
            return (
                ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY,
                selected_additional_columns,
            )
    else:
        if additional_columns_count > 0:
            return ColumnsStructure.INVALID_MULTI_COLUMN, []
        else:
            next_column_is_additional = False
            if column_index + 1 < columns_count:
                for (
                    additional_column_pattern
                ) in multiple_columns_additional_header_patterns:
                    if re.match(additional_column_pattern, columns[column_index + 1]):
                        next_column_is_additional = True
                        break
            if next_column_is_additional:
                return ColumnsStructure.INVALID_MULTI_COLUMN, []

    return ColumnsStructure.SINGLE_COLUMN, []


def select_additional_columns(column_index, columns: List[str]):
    for i in range(len(additional_column_templates)):
        template = additional_column_templates[i]
        next_item = column_index + 1
        maximum_match = 0
        matched = True
        internal_index = 0
        for pattern in template:
            if next_item >= len(columns) or not re.match(pattern, columns[next_item]):
                matched = False
                break
            next_item = next_item + 1
            internal_index = internal_index + 1
            if maximum_match < internal_index:
                maximum_match = internal_index

        if matched:
            return ADDITIONAL_COLUMN_HEADERS[i], maximum_match
    return [], maximum_match
