import os
import re
from io import TextIOWrapper
from typing import List, Tuple, Union

from pandas import DataFrame

from metabolights_utils.models.isa.common import IsaTableColumn, IsaTableFile
from metabolights_utils.models.isa.enums import (
    ColumnsStructure,
    IsaTableAdditionalColumn,
    ParserMessageType,
)
from metabolights_utils.models.isa.messages import ParserMessage
from metabolights_utils.models.isa.parser.common import read_table_file


def parse_isa_table_sheet_from_fs(
    file_path, expected_patterns: Union[None, List[List[str]]] = None, **kwargs
) -> Tuple[IsaTableFile, List[ParserMessage]]:
    basename = os.path.basename(file_path)
    dirname = os.path.basename(os.path.dirname(file_path))
    messages: List[ParserMessage] = []
    if not file_path:
        message = ParserMessage(short="File path is not valid", type=ParserMessageType.CRITICAL)
        message.detail = "File path is not valid"
        messages.append(message)
        return IsaTableFile(), messages

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        message = ParserMessage(
            short="File does not exist or it is not a file",
            type=ParserMessageType.CRITICAL,
        )
        message.detail = f"File does not exist or is not a file: {basename} in {dirname}"
        messages.append(message)
        return IsaTableFile(), messages

    file_size = os.stat(file_path).st_size
    if file_size == 0:
        message = ParserMessage(short="File is empty", type=ParserMessageType.CRITICAL)
        message.detail = f"File is empty: {basename} in {dirname}"
        messages.append(message)
        return IsaTableFile(), messages
    basename = os.path.basename(file_path)

    with open(file_path, "r") as f:
        read_messages: List[ParserMessage] = []
        isa_table = get_isa_table(
            basename,
            f,
            messages=read_messages,
            expected_patterns=expected_patterns,
            **kwargs,
        )
        if isa_table.table.columns:
            messages.extend(read_messages)
            messages = [x for x in messages if x.type != ParserMessageType.INFO]
            return isa_table, messages

    with open(file_path, "r", errors="backslashreplace") as f:
        read_messages = []
        isa_table = get_isa_table(
            basename,
            f,
            messages=read_messages,
            expected_patterns=expected_patterns,
            **kwargs,
        )
        isa_table.filePath = basename

        if isa_table.table.columns:
            message = ParserMessage(
                short="File is read utf-8 encoding and invalid characters errors are replaced with backslash",
                type=ParserMessageType.WARNING,
            )
            message.detail = (
                "Invalid characters are replaced with backslash characters: "
                + f"{basename} in {dirname}"
            )
            messages.append(message)
            messages.extend(read_messages)
            messages = [x for x in messages if x.type != ParserMessageType.INFO]
            return isa_table, messages
    messages = [x for x in messages if x.type != ParserMessageType.INFO]
    return isa_table, messages


def get_isa_table(
    file_name,
    file_path_or_buffer: TextIOWrapper,
    messages: List[ParserMessage],
    expected_patterns,
    **kwargs,
):
    study_table = IsaTableFile()
    if messages is None:
        messages = []
    if not expected_patterns:
        expected_patterns = []
    file_path_or_buffer.seek(0)
    df: DataFrame = read_table_file(
        file_name,
        file_path_or_buffer,
        messages,
        header=0,
        delimiter="\t",
        dtype=str,
        **kwargs,
    )
    if df is None:
        return study_table
    return update_isa_table_file(
        study_table,
        df,
        file_name,
        file_path_or_buffer,
        messages,
        expected_patterns,
        **kwargs,
    )


def update_isa_table_file(
    study_table: IsaTableFile,
    df: DataFrame,
    file_name: str,
    file_path_or_buffer: TextIOWrapper,
    messages: List[ParserMessage],
    expected_patterns,
    **kwargs,
):
    columns = list(df.columns)
    first_column_name = None
    for column_name in columns:
        if not first_column_name:
            first_column_name = column_name
        cleaned_column_name = get_cleaned_header(column_name)

        if not len(cleaned_column_name.strip()) or len(cleaned_column_name) != len(
            cleaned_column_name.strip()
        ):
            message = ParserMessage(type=ParserMessageType.ERROR)
            column_index = columns.index(column_name)
            message.column = str(column_index)
            if len(cleaned_column_name.strip()) > 0:
                message.short = "Column header starts or ends with space"
                message.detail = (
                    f"'{column_name}' header at column {column_index + 1} "
                    + "ends or starts with space."
                )
            else:
                message.short = "Column header is empty"
                message.detail = f"'{column_name}' header at column {column_index + 1}  is empty."
            messages.append(message)

    headers = get_headers(columns, expected_patterns=expected_patterns, messages=messages)
    study_table.table.headers = headers
    if first_column_name:
        file_path_or_buffer.seek(0)
        total_df: DataFrame = read_table_file(
            file_name,
            file_path_or_buffer,
            [],
            delimiter="\t",
            usecols=[first_column_name],
            dtype=str,
        )
        if total_df is not None:
            study_table.table.totalRowCount = len(total_df.index)
    if "skiprows" in kwargs and kwargs["skiprows"] and len(kwargs["skiprows"]) > 0:
        offset = len(kwargs["skiprows"])
        if offset < study_table.table.totalRowCount:
            study_table.table.rowOffset = len(kwargs["skiprows"])
        else:
            study_table.table.rowOffset = 0

    data = df.to_dict(orient="list")
    study_table.table.data = data
    study_table.table.columns = columns
    study_table.table.rowCount = len(df.index)
    study_table.filePath = file_name

    return study_table


MULTI_COLUMN_TEMPLATES = {
    ColumnsStructure.ONTOLOGY_COLUMN: {
        "columnNames": [
            IsaTableAdditionalColumn.TERM_SOURCE_REF,
            IsaTableAdditionalColumn.TERM_ACCSSION_NUMBER,
        ],
        "searchPatterns": [
            "(Term Source REF)(\.\d+)?",
            "(Term Accession Number)(\.\d+)?",
        ],
    },
    ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY: {
        "columnNames": [
            IsaTableAdditionalColumn.UNIT,
            IsaTableAdditionalColumn.TERM_SOURCE_REF,
            IsaTableAdditionalColumn.TERM_ACCSSION_NUMBER,
        ],
        "searchPatterns": [
            "(Unit)(\.\d+)?",
            "(Term Source REF)(\.\d+)?",
            "(Term Accession Number)(\.\d+)?",
        ],
    },
}

additional_column_templates = [
    MULTI_COLUMN_TEMPLATES[ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY]["searchPatterns"],
    MULTI_COLUMN_TEMPLATES[ColumnsStructure.ONTOLOGY_COLUMN]["searchPatterns"],
]

additional_column_headers = [
    MULTI_COLUMN_TEMPLATES[ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY]["columnNames"],
    MULTI_COLUMN_TEMPLATES[ColumnsStructure.ONTOLOGY_COLUMN]["columnNames"],
]

multiple_columns_additional_header_patterns = MULTI_COLUMN_TEMPLATES[
    ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY
]["searchPatterns"]


samples_file_expected_patterns = [
    ["^(Source Name)$", ""],
    ["^Characteristics\[(\w[ -~]*)\]$", "Characteristics"],
    ["^(Protocol REF)(\.\d+)?$", "Protocol"],
    ["^(Sample Name)$", ""],
    ["^Factor Value\[(\w[ -~]*)\]$", "Factor Value"],
    ["^Comment\b\[(\w{1}[ -~]*)\]$", "Comment"],
]

assay_file_expected_patterns = [
    ["^(Extract Name)$", ""],
    ["^(Protocol REF)(\.\d+)?$", "Protocol"],
    ["^(Sample Name)$", ""],
    ["^Parameter Value\[(\w[ -~]*)\]$", "Parameter Value"],
    ["^Comment\b\[(\w{1}[ -~]*)\]$", "Comment"],
    ["^(Labeled Extract Name)$", ""],
    ["^(Label)$", ""],
]


def get_cleaned_header(column_name):
    cleaned_column_name = column_name
    last_dot = column_name.rfind(".")
    if last_dot > 0:
        left = column_name[:last_dot]
        right = column_name[last_dot:].lstrip(".")
        if right and right.isnumeric():
            cleaned_column_name = left
    return cleaned_column_name


def get_headers(columns: List[str], expected_patterns, messages: List[ParserMessage]):
    headers = []
    column_index = 0
    columns_count = len(columns)
    while column_index < columns_count:
        column_name = columns[column_index]
        cleaned_column_name = get_cleaned_header(column_name)
        column_structure, additional_column_headers = define_column_structure(column_index, columns)

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

        column = IsaTableColumn(columnIndex=str(column_index), colummnStructure=column_structure)
        column.columnName = column_name
        column.columnHeader = cleaned_column_name
        linked_columns = []

        if column_structure == ColumnsStructure.ADDITIONAL_COLUMN:
            column.columnCategory = "Additional"
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
            column.additionalColumns = additional_column_headers
            additional_column_index = column_index

            for additional_column in column.additionalColumns:
                additional_column_index = additional_column_index + 1
                linked_column = IsaTableColumn(
                    columnIndex=str(additional_column_index),
                    colummnStructure=ColumnsStructure.LINKED_COLUMN,
                )
                linked_column.columnHeader = additional_column
                linked_column.columnCategory = "Linked Column"
                linked_column.columnName = columns[additional_column_index]
                linked_columns.append(linked_column)

            update_as_multi_column(
                expected_patterns,
                cleaned_column_name,
                pattern_index,
                expected_header,
                message,
                column,
            )
            column_index = column_index + len(additional_column_headers)

        headers.append(column)
        if linked_columns:
            headers.extend(linked_columns)

        update_message(messages, column_index, message, column)

        column_index = column_index + 1
    return headers


def update_message(messages, column_index, message, column):
    if not message.detail:
        column_message = " ".join(
            [
                f"Column {(column.columnIndex + 1):03}: '{column.columnCategory}' column",
                f"column name: '{column.columnHeader}'",
            ]
        )
        message.detail = column_message
    if not message.short:
        message.short = f"'{column.columnCategory}' column: '{column.columnHeader}'"
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
        column.columnSearchPattern = expected_patterns[pattern_index][0]
        column.columnCategory = expected_patterns[pattern_index][1]
        column.columnPrefix = expected_patterns[pattern_index][1]
    else:
        column.columnCategory = "Undefined"
        message.type = ParserMessageType.INFO
        message.short = f"Multi column '{cleaned_column_name}' is not in expected column list."


def update_as_invalid_column(
    expected_patterns,
    cleaned_column_name,
    pattern_index,
    expected_header,
    message: ParserMessage,
    column: IsaTableColumn,
):
    if expected_header:
        column.columnSearchPattern = expected_patterns[pattern_index][0]
        column.columnPrefix = expected_patterns[pattern_index][1]
        column.columnCategory = expected_patterns[pattern_index][1]
    else:
        column.columnCategory = "Invalid"
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
        column.columnSearchPattern = expected_patterns[pattern_index][0]
        column.columnCategory = expected_patterns[pattern_index][1]
        column.columnPrefix = expected_patterns[pattern_index][1]
    else:
        column.columnCategory = "Undefined"
        message.type = ParserMessageType.INFO
        message.short = f"Single column '{cleaned_column_name}' is not in expected column list."


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
                for additional_column_pattern in multiple_columns_additional_header_patterns:
                    if re.match(additional_column_pattern, columns[column_index + 1]):
                        next_column_is_additional = True
                        break
            if next_column_is_additional:
                return ColumnsStructure.INVALID_MULTI_COLUMN, []

    return ColumnsStructure.SINGLE_COLUMN, []


def select_additional_columns(column_index, columns: List[str]):
    for i in range(len(additional_column_templates)):
        template = additional_column_templates[i]
        next = column_index + 1
        maximum_match = 0
        matched = True
        internal_index = 0
        for pattern in template:
            if next >= len(columns) or not re.match(pattern, columns[next]):
                matched = False
                break
            next = next + 1
            internal_index = internal_index + 1
            if maximum_match < internal_index:
                maximum_match = internal_index

        if matched:
            return additional_column_headers[i], maximum_match
    return [], maximum_match
