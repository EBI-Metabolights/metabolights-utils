import logging
import pathlib
import re
import sys
from io import IOBase
from typing import Callable, Dict, List, Tuple, Union

from pydantic import BaseModel
from pydantic.alias_generators import to_snake

from metabolights_utils.isatab.default.parser.common import read_investigation_file
from metabolights_utils.models.isa import investigation_file
from metabolights_utils.models.isa.common import (
    INVESTIGATION_FILE_INITIAL_ROWS,
    INVESTIGATION_FILE_INITIAL_ROWS_SET,
    INVESTIGATION_FILE_SECTION_NAMES,
    INVESTIGATION_FILE_STUDY_ROWS,
    INVESTIGATION_FILE_STUDY_ROWS_SET,
    Comment,
    IsaAbstractModel,
)
from metabolights_utils.models.isa.investigation_file import (
    BaseSection,
    Investigation,
    Study,
)
from metabolights_utils.models.parser.common import ParserMessage
from metabolights_utils.models.parser.enums import ParserMessageType

logger = logging.getLogger(__name__)

model_module_name = investigation_file.__name__


def parse_investigation_file_content(
    parser: Callable,
    file_path: str,
    messages: List[ParserMessage],
    fix_unicode_exceptions: bool = False,
) -> Tuple[Investigation, List[ParserMessage]]:
    try:
        with pathlib.Path(file_path).open("r", encoding="utf-8") as f:
            model = parser(f, file_path, messages=messages)
            logger.debug("%s is loaded.", file_path)
            return model, messages
    except UnicodeDecodeError as ex:
        logger.warning("Unicode decode error for file %s: %s", file_path, str(ex))
        if fix_unicode_exceptions:
            try:
                with pathlib.Path(file_path).open("r", encoding="latin-1") as f:
                    model = parser(f, file_path, messages=messages)
                    message = ParserMessage(
                        short="File is read with latin-1 encoding",
                        type=ParserMessageType.WARNING,
                    )
                    message.detail = "File is read with latin-1 encoding"
                    messages.append(message)
                    return model, messages
            except Exception as ex:
                logger.exception("File read error for %s: %s", file_path, str(ex))
                message = ParserMessage(
                    short="File read exception", type=ParserMessageType.CRITICAL
                )
                message.detail = f"File parse error: {str(ex)}"
                messages.append(message)
                return None, messages
        else:
            logger.exception("File read error for %s: %s", file_path, str(ex))
            message = ParserMessage(
                short="File read exception", type=ParserMessageType.CRITICAL
            )
            message.detail = f"File parse error: {str(ex)}"
            messages.append(message)
            return None, messages

    except Exception as ex:
        logger.exception("File read error for %s: %s", file_path, str(ex))
        message = ParserMessage(
            short="File read exception", type=ParserMessageType.CRITICAL
        )
        message.detail = f"File parse error: {str(ex)}"
        messages.append(message)
        return None, messages


def parse_investigation_from_fs(
    file_path: str, fix_unicode_exceptions: bool = False
) -> Tuple[Union[Investigation, None], List[ParserMessage]]:
    messages: List[ParserMessage] = []
    file = pathlib.Path(file_path)
    basename = pathlib.Path(file).name
    if not file.exists():
        logger.error("File does not exist %s", basename)
        message = ParserMessage(
            short="File does not exist", type=ParserMessageType.CRITICAL
        )
        message.detail = f"File does not exist: {basename}"
        messages.append(message)
        return None, messages
    file_size = file.stat().st_size
    if file_size == 0:
        logger.error("File is empty: %s", basename)
        message = ParserMessage(short="File is empty", type=ParserMessageType.CRITICAL)
        message.detail = f"File is empty: {basename}"
        messages.append(message)
        return None, messages
    return parse_investigation_file_content(
        get_investigation, file_path, messages, fix_unicode_exceptions
    )


def get_investigation(
    file_buffer: IOBase, file_path: str, messages: List[ParserMessage]
):
    if messages is None:
        messages = []
    index_map = {}
    initial_part = []
    study_parts = []
    initial_part_index_map = {}
    study_parts_index_map = []
    study_parts_index_map = []
    ignore_comments = []
    initial_part_comments = {}
    current_study_part_comments = {}
    study_part_comment_list = []
    is_study_part = False
    current_section = ""
    result = None
    if file_buffer and isinstance(file_buffer, IOBase):
        result: Dict[int, Dict[int, str]] = read_investigation_file(
            file_buffer, messages
        )
    else:
        if (
            file_path
            and isinstance(file_path, pathlib.Path)
            or isinstance(file_path, str)
        ):
            with pathlib.Path(file_path).open("r", encoding="utf-8") as f:
                result: Dict[int, Dict[int, str]] = read_investigation_file(f, messages)

    if result is None:
        logger.warning("File %s is not valid", file_path)
        return Investigation()

    tab: Dict[int, Dict[int, str]] = result
    for line in tab.keys():
        if len(tab[line]) == 0:
            logger.warning("Empty line in file %s, line number: %s", str(line))
            messages.append(
                ParserMessage(
                    short="Empty line",
                    type=ParserMessageType.WARNING,
                    detail=f"Empty line in {str(line)}",
                    line=str(line),
                )
            )
            index_map[line] = ""
            continue
        index_string = tab[line][0]
        index_map[line] = index_string

        if (
            index_string not in INVESTIGATION_FILE_INITIAL_ROWS_SET
            and index_string not in INVESTIGATION_FILE_STUDY_ROWS_SET
        ):
            if index_string.startswith("#"):
                logger.debug(
                    "File comment in %s will be ignored. "
                    "Line number %s, starts with %s  ",
                    file_path,
                    str(line),
                    index_string,
                )
                ignore_comments.append(line)
                messages.append(
                    ParserMessage(
                        type=ParserMessageType.INFO,
                        short="File comment line",
                        detail=f"Comment at line {str(line)}:{index_string}",
                    )
                )
                continue
            if index_string.startswith("Comment"):
                if not is_study_part:
                    is_valid, message_detail = add_line_comment(
                        line, index_string, current_section, initial_part_comments, tab
                    )
                else:
                    is_valid, message_detail = add_line_comment(
                        line,
                        index_string,
                        current_section,
                        current_study_part_comments,
                        tab,
                    )
                if not is_valid:
                    logger.error("Invalid ISA comment line at %s", str(line))
                    message = ParserMessage(
                        short="Invalid ISA comment line", type=ParserMessageType.WARNING
                    )
                    message.detail = f"{message_detail}"
                    message.line = str(line)
                    messages.append(message)
                continue
            else:
                messages.append(
                    ParserMessage(
                        short="Invalid line",
                        type=ParserMessageType.ERROR,
                        detail=f"{index_string}",
                    )
                )
                continue

        if re.match(r"^[A-Z][A-Z0-9 ]+[A-Z0-9]$", index_string):
            current_section = index_string
            if index_string != "STUDY":
                continue

        if not current_section:
            message = ParserMessage(
                short="Invalid start section", type=ParserMessageType.ERROR
            )
            message.detail = (
                f"Line {str(line + 1)}: {index_string} is not valid section start"
            )
            messages.append(message)
            message.line = str(line)

        if not is_study_part:
            if index_string == "STUDY":
                is_study_part = True
            elif index_string not in INVESTIGATION_FILE_INITIAL_ROWS_SET:
                message = ParserMessage(
                    short="Unexpected line in the section", type=ParserMessageType.ERROR
                )
                message.detail = f"Unexpected line in {str(line + 1)}"
                message.line = str(line)
                messages.append(message)
                continue
            else:
                initial_part.append(index_string)
                initial_part_index_map[index_string] = line

        if is_study_part:
            new_study_part = False
            if index_string == "STUDY":
                new_study_part = True
                study_part = []
                study_part_index = {}
                study_part_comments = {}
                study_parts_index_map.append(study_part_index)
                study_part_comment_list.append(study_part_comments)
                current_study_part_comments = study_part_comments
                study_parts.append(study_part)

            if index_string not in INVESTIGATION_FILE_STUDY_ROWS_SET:
                message = ParserMessage(
                    short="Unexpected line in the study section",
                    type=ParserMessageType.ERROR,
                )
                message.detail = f"Unexpected line in {str(line + 1)}"
                message.line = str(line)
                messages.append(message)
                continue
            if study_part or new_study_part:
                study_part.append(index_string)
                study_part_index[index_string] = line

    studies = build_studies(
        file_path,
        messages,
        study_parts,
        study_parts_index_map,
        study_part_comment_list,
        tab,
    )

    investigation, _ = build_investigation(
        file_path,
        initial_part_index_map,
        tab,
        studies,
        initial_part_comments,
        messages=messages,
    )
    investigation.sync_fields_from_comments()
    return investigation


def build_studies(
    source, messages, study_parts, study_parts_index_map, study_part_comment_list, tab
):
    studies = []

    if study_parts:
        for i in range(len(study_parts)):
            study, _ = build_study(
                source,
                study_parts_index_map[i],
                tab,
                messages=messages,
                comments_map=study_part_comment_list[i],
            )
            studies.append(study)
    return studies


def add_line_comment(line_index, line, current_section, comments_list, table):
    val = ""
    try:
        result = re.search(r"^Comment ?\[(.+)\]$", line or "")

        if result and result.groups():
            val = result.group(1)
        else:
            return None, "Not a valid comment line"

    except Exception as ex:
        return None, f"Invalid comment line format {line} {str(ex)}"

    if current_section not in comments_list:
        comments_list[current_section] = []
    values = [table[line_index][i] for i in range(1, len(table[line_index]))]

    comments_list[current_section].append((val, values))
    return result, f"Comment Name:'{val}' Value:'{table[line_index][1]}'"


def build_study(
    file_path,
    index_map: dict,
    content: dict,
    comments_map: dict,
    messages: Union[None, List[ParserMessage]] = None,
):
    study: Study = Study()

    missing_rows = [
        x
        for x in INVESTIGATION_FILE_STUDY_ROWS
        if x not in index_map and x not in INVESTIGATION_FILE_SECTION_NAMES
    ]
    if missing_rows:
        message = ParserMessage(
            short=f"Some rows are missing for study: {', '.join(missing_rows)}",
            type=ParserMessageType.CRITICAL,
        )
        message.detail = "Investigation file is not complete."
        messages.append(message)
        return study, messages
    extra_rows = [
        x
        for x in index_map
        if x not in INVESTIGATION_FILE_STUDY_ROWS
        and not x.lower().startswith(
            "comment[" and x not in INVESTIGATION_FILE_SECTION_NAMES
        )
    ]
    if extra_rows:
        row_messages = ", ".join([f"Line {index_map[x]}:{x}" for x in extra_rows])
        message = ParserMessage(
            short=f"Some rows are missing for study: {row_messages}",
            type=ParserMessageType.CRITICAL,
        )
        message.detail = "Investigation file has unexpected rows."
        messages.append(message)

    assign_by_field_name(
        file_path,
        study,
        index_map,
        content,
        comments_map=comments_map,
        messages=messages,
    )
    return study, messages


def build_investigation(
    file_path,
    index_map: dict,
    content: dict,
    studies: List[Study],
    comments_map: dict,
    messages: Union[None, List[ParserMessage]] = None,
):
    messages = messages if messages is not None else []
    investigation: Investigation = Investigation()

    missing_rows = [
        x
        for x in INVESTIGATION_FILE_INITIAL_ROWS
        if x not in index_map and x not in INVESTIGATION_FILE_SECTION_NAMES
    ]
    if missing_rows:
        message = ParserMessage(
            short=f"Some rows are missing for investigation: {', '.join(missing_rows)}",
            type=ParserMessageType.CRITICAL,
        )
        message.detail = "Investigation file is not complete."
        messages.append(message)
        return investigation, messages

    extra_rows = [
        x
        for x in index_map
        if x not in INVESTIGATION_FILE_INITIAL_ROWS
        and not x.lower().startswith(
            "comment[" and x not in INVESTIGATION_FILE_SECTION_NAMES
        )
    ]
    if extra_rows:
        row_messages = ", ".join([f"Line {index_map[x]}:{x}" for x in extra_rows])
        message = ParserMessage(
            short=f"Some rows are missing for study: {row_messages}",
            type=ParserMessageType.CRITICAL,
        )
        message.detail = "Investigation file has unexpected lines."
        messages.append(message)

    assign_by_field_name(
        file_path,
        investigation,
        index_map,
        content,
        comments_map=comments_map,
        messages=messages,
    )
    investigation.studies = studies
    return investigation, messages


def set_value(obj, key, value):
    camel_key = to_snake(key)
    setattr(obj, camel_key, value)


def assign_by_field_name(
    file_path,
    data: BaseModel,
    index_map: dict,
    tab: dict,
    messages: List[ParserMessage],
    prefix="",
    value_index=1,
    comments_map=None,
) -> None:
    if messages is None:
        messages = []
    data_schema = data.model_json_schema()
    if "properties" not in data_schema or not data_schema["properties"]:
        logger.debug("Properties are not defined in %s", file_path)
        message = ParserMessage(
            short="Property is not defined for object", type=ParserMessageType.WARNING
        )
        message.detail = f"{data.__repr_name__} values will not assigned."
        messages.append(message)
        return

    initial_name_prefix = prefix or ""
    section_prefix = ""
    if isinstance(data, BaseSection):
        section: BaseSection = data
        prefix_value = section.isatab_config.section_prefix
        section_prefix = prefix_value.strip() if prefix_value else ""
        initial_name_prefix = (
            section_prefix
            if not initial_name_prefix
            else f"{initial_name_prefix.strip()} {section_prefix}".strip()
        )
    if isinstance(data, BaseSection) and comments_map:
        section: BaseSection = data
        section_header = section.isatab_config.section_header or ""
        if section_header in comments_map and comments_map[section_header]:
            section.comments = []
            for comment in comments_map[section_header]:
                section.comments.append(Comment(name=comment[0], value=comment[1]))

    for key in data_schema["properties"]:
        if (
            key not in data_schema["properties"]
            or not data_schema["properties"][key]
            or (
                "auto_fill" in data_schema["properties"]
                and data_schema["properties"]["auto_fill"]
            )
        ):
            continue

        field_definition = data_schema["properties"][key]

        field_name = ""
        data_type = "invalid"
        ref_object_definition = ""
        name_prefix = initial_name_prefix

        if (
            "inherit_prefix" in field_definition
            and not field_definition["inherit_prefix"]
        ):
            name_prefix = prefix.strip() if prefix else ""

        if "$ref" in field_definition and field_definition["$ref"]:
            data_type = "ref"
            ref_object_definition = field_definition["$ref"]
        elif "allOf" in field_definition and field_definition["allOf"]:
            if (
                "$ref" in field_definition["allOf"][0]
                and field_definition["allOf"][0]["$ref"]
            ):
                data_type = "ref"
                ref_object_definition = field_definition["allOf"][0]["$ref"]
        elif "anyOf" in field_definition and field_definition["anyOf"]:
            primitives = {"string", "int", "float"}
            for field_item in field_definition["anyOf"]:
                if "type" in field_item and field_item["type"] in primitives:
                    data_type = "string"
                    break
        elif "type" in field_definition:
            data_type = field_definition["type"]
        text_multiple_value = False
        if (
            "text_multiple_value" in field_definition
            and field_definition["text_multiple_value"]
        ):
            text_multiple_value = True
        if field_definition and "header_name" in field_definition:
            if (
                "section_prefix" in field_definition
                and field_definition["section_prefix"]
            ):
                field_name = " ".join(
                    [
                        f"{name_prefix}",
                        f"{field_definition['section_prefix']}",
                        f"{field_definition['header_name']}",
                    ]
                ).strip()
            else:
                field_name = f"{name_prefix} {field_definition['header_name']}".strip()
            if data_type == "array" and not text_multiple_value:
                if "items" in field_definition and field_definition["items"]:
                    items = field_definition["items"]
                    if "$ref" in items and items["$ref"]:
                        search_field = field_name
                        if "search_header" in field_definition:
                            # if (
                            #     "section_prefix" in field_definition
                            #     and field_definition["section_prefix"]
                            # ):
                            #     search_field = " ".join(
                            #         [
                            #             name_prefix,
                            #             field_definition["section_prefix"],
                            #             field_definition["search_header"],
                            #         ]
                            #     )
                            # else:
                            search_field = (
                                f"{name_prefix} {field_definition['search_header']}"
                            )

                        item_list = []
                        set_value(data, key, item_list)

                        if search_field not in index_map:
                            logger.debug(
                                "%s is not in file. Skipping %s in %s",
                                search_field,
                                field_name,
                                file_path,
                            )
                            continue
                        index = index_map[search_field]

                        max_index = len(tab[index])
                        ref_class_name = (
                            items["$ref"]
                            .replace("#/definitions/", "")
                            .replace("#/$defs/", "")
                        )
                        ref_class = getattr(
                            sys.modules[model_module_name],
                            ref_class_name,
                        )
                        for i in range(1, max_index):
                            instance = ref_class()
                            item_list.append(instance)
                            assign_by_field_name(
                                file_path,
                                instance,
                                index_map,
                                tab,
                                prefix=field_name,
                                value_index=i,
                                messages=messages,
                                comments_map=comments_map,
                            )

                        count = len(item_list)
                        for i in range(count):
                            instance_item = item_list[count - i - 1]
                            if IsaAbstractModel.is_empty_model(model=instance_item):
                                item_list.pop()
                            else:
                                break
            elif data_type == "array" and text_multiple_value:
                if "items" in field_definition and field_definition["items"]:
                    items = field_definition["items"]
                    if "$ref" in items and items["$ref"]:
                        ref_class_name = (
                            items["$ref"]
                            .replace("#/definitions/", "")
                            .replace("#/$defs/", "")
                        )
                        ref_class = getattr(
                            sys.modules[model_module_name],
                            ref_class_name,
                        )
                        instance = ref_class()
                        set_value(data, key, [instance])
                        assign_by_field_name(
                            file_path,
                            instance,
                            index_map,
                            tab,
                            prefix=field_name,
                            value_index=value_index,
                            messages=messages,
                            comments_map=comments_map,
                        )
                        item_schema = instance.model_json_schema()

                        new_instances = []
                        separator = ";"
                        for item_key in item_schema["properties"]:
                            item_field_definition = item_schema["properties"][item_key]
                            if (
                                not item_field_definition
                                or "auto_fill" not in item_field_definition
                                or not item_field_definition["auto_fill"]
                            ):
                                continue
                            if (
                                "seperator" in item_field_definition
                                and item_field_definition["seperator"]
                            ):
                                separator = item_field_definition["seperator"]
                            attribute_key = to_snake(item_key)
                            item_val = getattr(instance, attribute_key) or ""
                            separated_values = item_val.split(separator)
                            for _ in range(len(separated_values)):
                                instance_count = len(new_instances)
                                values_count = len(separated_values)
                                if instance_count < values_count:
                                    for _ in range(instance_count, values_count):
                                        new_instances.append(ref_class())
                                for j in range(values_count):
                                    set_value(
                                        new_instances[j], item_key, separated_values[j]
                                    )
                        count = len(new_instances)
                        for i in range(len(new_instances)):
                            instance_item = new_instances[count - i - 1]
                            if IsaAbstractModel.is_empty_model(model=instance_item):
                                new_instances.pop()
                            else:
                                break
                        set_value(data, key, new_instances)
                    else:
                        message = ParserMessage(
                            short="Reference item is not valid",
                            type=ParserMessageType.WARNING,
                        )
                        message.detail = f"Reference item is not valid {data_type} "
                        messages.append(message)
                        logger.debug("Reference item is not valid")
                else:
                    message = ParserMessage(
                        short="There is not item", type=ParserMessageType.WARNING
                    )
                    message.detail = "There is not item"
                    messages.append(message)
                    logger.debug("There is not item")
            elif data_type == "string":
                if field_name not in index_map:
                    message = ParserMessage(
                        short="Index is not defined", type=ParserMessageType.WARNING
                    )
                    message.detail = f"{field_name} is not in {file_path}. "
                    messages.append(message)
                    logger.warning("%sis not in %s Skipping", field_name, file_path)
                    set_value(data, key, "")
                    continue
                index = index_map[field_name]
                value = ""
                if len(tab[index]) > value_index:
                    value = tab[index][value_index]
                else:
                    value = ""
                set_value(data, key, str(value).strip('"').strip() or "")
            elif data_type == "ref":
                ref_class_name = ref_object_definition.replace(
                    "#/definitions/", ""
                ).replace("#/$defs/", "")
                ref_class = getattr(sys.modules[model_module_name], ref_class_name)
                instance = ref_class()
                set_value(data, key, instance)
                assign_by_field_name(
                    file_path,
                    instance,
                    index_map,
                    tab,
                    prefix=field_name,
                    value_index=value_index,
                    messages=messages,
                    comments_map=comments_map,
                )
            else:
                if data_type:
                    message = ParserMessage(
                        short="Invalid data type", type=ParserMessageType.ERROR
                    )
                    message.detail = f"Invalid data type {data_type} in {file_path}"
                    messages.append(message)
                else:
                    message = ParserMessage(
                        short=f"Invalid data type in {file_path}",
                        type=ParserMessageType.ERROR,
                    )
                    message.detail = "Data type is not valid"
                    messages.append(message)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    model, messages = parse_investigation_from_fs(
        "tests/test-data/MTBLS60/i_Investigation.txt"
    )
