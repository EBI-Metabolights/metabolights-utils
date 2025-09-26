import logging
import re
import sys
from functools import reduce
from io import IOBase, TextIOWrapper
from typing import Dict, List, Union

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.isa.common import (
    INVESTIGATION_FILE_INITIAL_ROWS_SET,
    INVESTIGATION_FILE_STUDY_ROWS_SET,
)
from metabolights_utils.models.parser.common import ParserMessage
from metabolights_utils.models.parser.enums import ParserMessageType
from metabolights_utils.tsv.filter import Filter, FilterRegistry, TsvFileFilterOption
from metabolights_utils.tsv.sort import Sorter, SorterRegistry, TsvFileSortOption

logger = logging.getLogger()


def read_investigation_file(file_buffer: IOBase, messages: List[ParserMessage]):
    new_lines = read_investigation_file_lines(file_buffer, messages)
    dict_format = {}
    for i in range(len(new_lines)):
        detail = {}
        for j in range(len(new_lines[i])):
            detail[j] = new_lines[i][j]
        dict_format[i] = detail

    return dict_format


def read_investigation_file_lines(file_buffer: IOBase, messages: List[ParserMessage]):
    new_lines: List[List[str]] = []
    try:
        lines = file_buffer.readlines()

        content = "".join(lines)
        line_separation = content.split("\n")
        richtext_lines = None
        tracked_lines = []
        for token in line_separation:
            if not token:
                continue
            cleared_item = token.split("\t")[0]
            if (
                cleared_item in INVESTIGATION_FILE_STUDY_ROWS_SET
                or cleared_item in INVESTIGATION_FILE_INITIAL_ROWS_SET
                or cleared_item.startswith("Comment")
            ):
                if richtext_lines:
                    if not tracked_lines:
                        tracked_lines.append("")
                    tracked_lines[-1] = (
                        tracked_lines[-1] + "\n" + "\n".join(richtext_lines)
                    )
                    richtext_lines = []

                tracked_lines.append(token.replace("Comment ", "Comment", 1))
            else:
                if not richtext_lines:
                    richtext_lines = []
                richtext_lines.append(token)
        if richtext_lines:
            message = ParserMessage(type=ParserMessageType.WARNING)
            lines = {"\n".join(richtext_lines)}
            message.short = f"Invalid end of file. {lines}"
            message.detail = "Returned result is not complete."
            messages.append(message)

        for line in tracked_lines:
            result = line.split("\t")
            cleared_lines: List[str] = []

            first_item = result[0]
            for item in result:
                complete_line = False
                if cleared_lines:
                    previous: str = cleared_lines[-1]
                    if (
                        previous.startswith('"')
                        and len(previous) > 1
                        and previous.endswith('"')
                    ) or (not previous.startswith('"')):
                        complete_line = True
                else:
                    complete_line = True
                if complete_line:
                    cleared_lines.append(item)
                else:
                    cleared_lines[-1] = cleared_lines[-1] + "\t" + item

            result = cleared_lines
            result.remove(result[0])

            values = []
            values.append(first_item)
            for item in result:
                value = re.sub(r"\s+", " ", item).strip('"').strip()
                if value != item.strip('"'):
                    old = re.sub(r"\n", "<!new line char>", item)
                    old = re.sub(r"\t", "<!tab char>", old)

                    message = ParserMessage(type=ParserMessageType.WARNING)
                    short = "\n".join(
                        [
                            f"Line '{first_item}' is updated. "
                            "Whitespace characters are removed",
                            f"Old: '{old}'",
                            f"New: '{value}'",
                        ]
                    )
                    message.short = short
                    message.detail = "Returned result is not complete."
                    messages.append(message)
                values.append(value.strip('"'))
            new_lines.append(values)
    except Exception as exc:
        message = ParserMessage(type=ParserMessageType.CRITICAL)
        message.short = f"The file can not read successfully. {str(exc)}"
        message.detail = f"Returned result is not complete. {str(exc)}"
        messages.append(message)

    for item in new_lines:
        new_line: List[str] = item
        if len(new_line) == 1 and not new_line[0].isupper():
            new_line.append('""')
    return new_lines


class TsvColumn(MetabolightsBaseModel):
    column_index: int = 0
    column_name: str = ""
    column_header: str = ""
    rows: Dict[int, str] = {}


class SelectedTsvFileContent(MetabolightsBaseModel):
    columns: List[TsvColumn] = []
    total_rows: int = 0
    total_filtered_rows: int = 0
    offset: int = 0
    limit: int = 0
    selected_column_count: int = 0
    total_columns: int = 0
    filter_options: List[TsvFileFilterOption] = []
    sort_options: List[TsvFileSortOption] = []


def read_table_file(
    file_buffer: TextIOWrapper,
    messages: List[ParserMessage],
    selected_columns: Union[None, List[str]] = None,
    offset: Union[int, None] = None,
    limit: Union[int, None] = None,
    filter_options: List[TsvFileFilterOption] = None,
    sort_options: List[TsvFileSortOption] = None,
) -> SelectedTsvFileContent:
    file_buffer.seek(0)
    file_content = file_buffer.read()
    find_empty_lines = re.findall(r"[\r\n][\r\n]+", file_content)
    if find_empty_lines:
        messages.append(
            ParserMessage(
                type=ParserMessageType.WARNING,
                short="Removed empty lines.",
                detail="Removed empty lines.",
            )
        )
        file_content = re.sub(r"[\r\n][\r\n]+", r"\n", file_content)
    pattern = r'(")([^"]*)\1(\t|\r|\n|$)'
    find_matches = re.findall(pattern, file_content)

    if find_matches:
        results = []

        def replace(x: re.Match):
            groups = x.groups()
            input_val = x.group()
            val = re.sub(r"\s", " ", groups[1].strip())

            result = groups[0] + val + groups[0] + groups[2]
            if result != input_val:
                results.append((groups[1], val))
            return result

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
                    short="Removed new line characters and "
                    "unexpected whitespaces in cells.",
                    detail=f"{str(printed_result)}",
                )
            )
            file_content = new_file_content

    file_lines = file_content.split("\n")
    if file_lines and file_lines[-1] == "":
        file_lines = file_lines[:-1]
    total_line = len(file_lines)
    total_data_rows = total_line - 1
    file_buffer.seek(0)
    rows = [[y.strip().strip('"') for y in x.split("\t")] for x in file_lines]
    if total_line == 0:
        raise ValueError("There is no row in file")
    content: SelectedTsvFileContent = SelectedTsvFileContent()
    content.total_rows = total_data_rows
    content.filter_options = filter_options if filter_options else []
    content.sort_options = sort_options if sort_options else []
    if filter_options or sort_options:
        return read_table_file_with_filter_and_sort_option(
            rows,
            content,
            messages,
            selected_columns,
            offset,
            limit,
            filter_options,
            sort_options,
        )

    content.total_filtered_rows = total_data_rows
    offset = 0 if not offset else offset

    content.offset = (
        offset if offset < content.total_filtered_rows else content.total_filtered_rows
    )

    if content.offset < 0:
        content.offset = 0
    remaining_row_count = content.total_filtered_rows - content.offset

    if limit is None:
        content.limit = (
            remaining_row_count
            if remaining_row_count <= content.total_filtered_rows
            else content.total_filtered_rows
        )
    else:
        content.limit = remaining_row_count if remaining_row_count < limit else limit

    if content.limit < 0:
        content.limit = 0

    columns: Dict[str, TsvColumn] = {}
    column_indices: Dict[int, str] = {}
    selected_column_indices: Dict[int, str] = {}
    column_name_indices: Dict[str, int] = {}

    try:
        next_row_index = 0
        skipped_rows = 0
        read_rows = 0
        for row in rows:
            next_row_index += 1
            row_index = next_row_index - 1
            if row_index == 0:
                read_tsv_file_header(
                    content,
                    row,
                    selected_columns,
                    columns,
                    column_indices,
                    column_name_indices,
                    selected_column_indices,
                )
            else:
                if offset and skipped_rows < offset:
                    skipped_rows += 1
                    continue
                read_next_row = True
                if isinstance(limit, int) and read_rows >= limit:
                    read_next_row = False
                if read_next_row:
                    read_rows += 1
                    add_tsv_file_data_row(
                        row,
                        row_index - 1,
                        columns,
                        selected_column_indices=selected_column_indices,
                    )
                else:
                    break

    except Exception as exc:
        message = ParserMessage(type=ParserMessageType.CRITICAL)
        message.short = "ISA table file can not be read successfully."
        message.detail = f"Returned result is not complete. {str(exc)}"
        messages.append(message)
        return SelectedTsvFileContent()
    return content


def read_table_file_with_filter_and_sort_option(
    rows: List[List[str]],
    content: SelectedTsvFileContent,
    messages: List[ParserMessage],
    selected_columns: Union[None, List[str]] = None,
    offset: Union[int, None] = None,
    limit: Union[int, None] = None,
    filter_options: List[TsvFileFilterOption] = None,
    sort_options: List[TsvFileSortOption] = None,
) -> SelectedTsvFileContent:
    columns: Dict[str, TsvColumn] = {}
    column_indices: Dict[int, str] = {}
    selected_column_indices: Dict[int, str] = {}
    column_name_indices: Dict[str, int] = {}
    filters: List[Filter] = []

    try:
        next_row_index = 0
        filtered_rows = []
        for row in rows:
            next_row_index += 1
            row_index = next_row_index - 1
            if row_index == 0:
                read_tsv_file_header(
                    content,
                    row,
                    selected_columns,
                    columns,
                    column_indices,
                    column_name_indices,
                    selected_column_indices,
                )
                if filter_options:
                    for filter_option in filter_options:
                        filter_option.search_columns = (
                            filter_option.search_columns
                            if filter_option.search_columns
                            else []
                        )
                        selected_filter: Filter = FilterRegistry.get_filter(
                            filter_option, column_name_indices, column_indices
                        )
                        filters.append(selected_filter)
                    # empty search column filters will be moved to end
                    filters.sort(
                        key=lambda x: (
                            len(x.filter_option.search_columns)
                            if x.filter_option.search_columns
                            else sys.maxsize
                        )
                    )
            else:
                if not filter_options:
                    filtered_rows.append((row_index - 1, row))
                else:
                    select: bool = True
                    for selected_filter in filters:
                        select = selected_filter.filter(row)
                        if not select:
                            break
                    if select:
                        filtered_rows.append((row_index - 1, row))
        rows = None

        sorters: List[Sorter] = []
        if sort_options:
            for sort_option in sort_options:
                col_index = column_name_indices[sort_option.column_name]
                sorter: Sorter = SorterRegistry.get_sorter(
                    sort_option,
                    col_index,
                    column_name_indices,
                    column_indices,
                )
                sorters.append(sorter)
        if sorters:
            filtered_rows = reduce(
                lambda s, sorter: sorted(
                    s, key=sorter.sort, reverse=sorter.sort_option.reverse
                ),
                reversed(sorters),
                filtered_rows,
            )

        content.total_filtered_rows = len(filtered_rows)
        offset = 0 if not offset else offset

        content.offset = (
            offset
            if offset < content.total_filtered_rows
            else content.total_filtered_rows
        )
        remaining_row_count = content.total_filtered_rows - content.offset
        if limit is None:
            content.limit = (
                remaining_row_count
                if remaining_row_count <= content.total_filtered_rows
                else content.total_filtered_rows
            )
        else:
            content.limit = (
                remaining_row_count if remaining_row_count < limit else limit
            )

        skipped_rows = 0
        read_rows = 0
        for data_row_index, row in filtered_rows:
            if offset and skipped_rows < offset:
                skipped_rows += 1
                continue
            read_next_row = True
            if isinstance(limit, int) and read_rows >= limit:
                read_next_row = False
            if read_next_row:
                read_rows += 1
                add_tsv_file_data_row(
                    row,
                    data_row_index,
                    columns,
                    selected_column_indices=selected_column_indices,
                )
            else:
                break

    except Exception as exc:
        message = ParserMessage(type=ParserMessageType.CRITICAL)
        message.short = "ISA table file can not be read successfully."
        message.detail = f"Returned result is not complete. {str(exc)}"
        messages.append(message)
    return content


def add_tsv_file_data_row(
    data_row,
    row_index: int,
    columns: Dict[str, TsvColumn],
    selected_column_indices: Dict[int, str],
):
    for column_index in selected_column_indices:
        column = columns[selected_column_indices[column_index]]
        column.rows[row_index] = data_row[column_index]


def prepare_column_names(
    selected_column_names: Union[None, List[str]],
    header_row: List[str],
    column_indices: Dict[int, str],
    column_name_indices: Dict[str, int],
):
    column_headers: Dict[str, int] = {}
    col_index = 0
    for col_index in range(len(header_row)):
        column_header = header_row[col_index]
        if column_header not in column_headers:
            column_headers[column_header] = 1
        else:
            column_headers[column_header] = column_headers[column_header] + 1

        column_name = (
            f"{column_header}.{(column_headers[column_header] - 1)}"
            if column_headers[column_header] > 1
            else column_header
        )
        column_name_indices[column_name] = col_index
        column_indices[col_index] = column_name
    new_ordered_columns = []
    invalid_column_names = []
    if selected_column_names is not None:
        for name in selected_column_names:
            if name in new_ordered_columns:
                continue
            if name == "Unit" or name.startswith("Unit."):
                continue
            elif name == "Term Source REF" or name.startswith("Term Source REF."):
                continue
            elif name == "Term Accession Number" or name.startswith(
                "Term Accession Number."
            ):
                continue
            elif name not in column_name_indices:
                invalid_column_names.append(name)
                continue
            else:
                new_ordered_columns.append(name)
                col_index = column_name_indices[name]
                term_source_relative_index = 1
                if col_index + 1 < len(header_row):
                    next_item: str = column_indices[col_index + 1]
                    if next_item == "Unit" or next_item.startswith("Unit."):
                        new_ordered_columns.append(next_item)
                        term_source_relative_index = 2

                if col_index + term_source_relative_index + 1 < len(header_row):
                    next_item: str = column_indices[
                        col_index + term_source_relative_index
                    ]
                    if next_item == "Term Source REF" or next_item.startswith(
                        "Term Source REF."
                    ):
                        new_ordered_columns.append(next_item)
                        next_item: str = column_indices[
                            col_index + term_source_relative_index + 1
                        ]
                        if next_item == "Term Accession Number" or next_item.startswith(
                            "Term Accession Number."
                        ):
                            new_ordered_columns.append(next_item)
        selected_column_names.clear()
        selected_column_names.extend(new_ordered_columns)
    if invalid_column_names:
        raise TypeError(
            "Column(s) do(es) not exist: " + ", ".join(invalid_column_names)
        )


def read_tsv_file_header(
    content: SelectedTsvFileContent,
    header_row,
    column_names: Union[None, List[str]],
    columns: Dict[str, TsvColumn],
    column_indices: Dict[int, str],
    column_name_indices: Dict[str, int],
    selected_column_indices: Dict[str, int],
):
    prepare_column_names(column_names, header_row, column_indices, column_name_indices)
    content.selected_column_count = len(column_names) if column_names else 0
    content.total_columns = len(header_row) if header_row else 0

    try:
        if column_names:
            for column_name in column_names:
                col_index = column_name_indices[column_name]
                column_header = header_row[col_index]
                column = TsvColumn(
                    column_index=col_index,
                    column_header=column_header,
                    column_name=column_name,
                )
                columns[column_name] = column
                selected_column_indices[col_index] = column_name
                content.columns.append(column)
        else:
            for col_index in range(len(header_row)):
                column_name = column_indices[col_index]
                column_header = header_row[col_index]
                column = TsvColumn(
                    column_index=col_index,
                    column_header=column_header,
                    column_name=column_name,
                )
                columns[column_name] = column
                selected_column_indices[col_index] = column_name
                content.columns.append(column)
    except Exception as exc:
        raise exc
