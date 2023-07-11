import re
from io import TextIOWrapper
from typing import List, Union

import pandas as pd

from metabolights_utils.models.isa.enums import ParserMessageType
from metabolights_utils.models.isa.investigation_file import (
    INVESTIGATION_FILE_INITIAL_ROWS_SET,
    INVESTIGATION_FILE_STUDY_ROWS_SET,
)
from metabolights_utils.models.isa.messages import ParserMessage


def read_investigation_file(file_name, file_path_or_buffer, messages: List[ParserMessage]):
    new_lines = read_investigation_file_lines(file_name, file_path_or_buffer, messages)
    dict_format = {}
    for i in range(len(new_lines)):
        detail = {}
        for j in range(len(new_lines[i])):
            detail[j] = new_lines[i][j]
        dict_format[i] = detail

    return dict_format


def read_investigation_file_lines(file_name, file: TextIOWrapper, messages: List[ParserMessage]):
    new_lines: List[List[str]] = []
    try:
        lines = file.readlines()

        content = "".join(lines)
        line_seperation = content.split("\n")
        richtext_lines = None
        tracked_lines = []
        for token in line_seperation:
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
                    tracked_lines[-1] = tracked_lines[-1] + "\n" + "\n".join(richtext_lines)
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
                        previous.startswith('"') and len(previous) > 1 and previous.endswith('"')
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
                            f"Line '{first_item}' is updated. Whitespace characters are removed",
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
        message.short = f"The file {file_name} can not read successfully. {str(exc)}"
        message.detail = "Returned result is not complete."
        messages.append(message)

    for item in new_lines:
        line: List[str] = item
        if len(line) == 1 and not line[0].isupper():
            line.append('""')
    return new_lines


def read_table_file(
    file_name, file_path_or_buffer, messages: List[ParserMessage], **kwargs
) -> Union[None, pd.DataFrame]:
    try:
        df = pd.read_csv(file_path_or_buffer, **kwargs)
        if df is not None:
            df = df.fillna("")

            return df
        message = ParserMessage(type=ParserMessageType.CRITICAL)
        message.short = f"The file {file_name} can not read successfully with utf-8 encoding."
        message.detail = "Returned result is empty."
        messages.append(message)
        return df
    except UnicodeDecodeError as ex:
        try:
            df = pd.read_csv(
                file_path_or_buffer,
                encoding="latin-1",
                encoding_errors="backslashreplace",
                **kwargs,
            )
            if df is not None:
                df = df.fillna("")
                message = ParserMessage(type=ParserMessageType.WARNING)
                message.short = (
                    f"The file {file_name} can not be opened with utf-8 encoding, "
                    + "it is opened using latin-1 encoding"
                )
                message.detail = str(ex)
                messages.append(message)
            message = ParserMessage(type=ParserMessageType.CRITICAL)
            message.short = (
                f"The file {file_name} is read with latin-1 encoding. "
                + "This may cause unexpected results!"
            )
            message.detail = "Returned result is empty."
            messages.append(message)
            return df

        except Exception as ex:
            message = ParserMessage(type=ParserMessageType.CRITICAL)
            message.short = f"The file {file_name} - can not be opened and read in latin-1 encoding"
            message.detail = str(ex)
            messages.append(message)
            return None
    except Exception as ex:
        message = ParserMessage(type=ParserMessageType.CRITICAL)
        message.short = f"The file {file_name} can not be opened: - {str(ex)}"
        message.detail = str(ex)
        messages.append(message)
        return None
