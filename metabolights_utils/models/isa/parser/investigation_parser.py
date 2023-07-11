import os
import re
import sys
from typing import Dict, List, Tuple, Union

from pydantic import BaseModel

from metabolights_utils.models.isa import investigation_file as model
from metabolights_utils.models.isa.common import Comment, IsaAbstractModel
from metabolights_utils.models.isa.enums import ParserMessageType
from metabolights_utils.models.isa.messages import ParserMessage
from metabolights_utils.models.isa.parser.common import read_investigation_file

model_module_name = model.__name__


def parse_investigation_from_fs(
    file_path,
) -> Tuple[Union[model.Investigation, None], List[ParserMessage]]:
    messages: List[ParserMessage] = []
    basename = os.path.basename(file_path)
    if not os.path.exists(file_path):
        print(f"File does not exist: {basename}")
        message = ParserMessage(short="File does not exist", type=ParserMessageType.CRITICAL)
        message.detail = f"File does not exist: {basename}"
        messages.append(message)
        return None, messages
    file_size = os.stat(file_path).st_size
    if file_size == 0:
        print(f"File is empty: {basename}")
        message = ParserMessage(short="File is empty", type=ParserMessageType.CRITICAL)
        message.detail = f"File is empty: {basename}"
        messages.append(message)
        return None, messages

    with open(file_path, "r") as f:
        investigation = get_investigation(basename, f, file_path, messages=messages)
        return investigation, messages


def get_investigation(file_name, file_path_or_buffer, source, messages: List[ParserMessage]):
    if messages is None:
        messages = []
    index_map = {}
    initial_part = []
    study_parts = []
    initial_part_index_map = {}
    study_parts_index_map = []
    study_parts_index_map = []
    ignore_comments = []
    inital_part_comments = {}
    study_part_comment = {}
    study_part_comment_list = []
    is_study_part = False
    current_section = ""

    result: Dict[int, Dict[int, str]] = read_investigation_file(
        file_name, file_path_or_buffer, messages
    )
    if result is None:
        return model.Investigation()

    tab: Dict[int, Dict[int, str]] = result
    for line in tab.keys():
        if len(tab[line]) == 0:
            message = ParserMessage(short="Empty line", type=ParserMessageType.WARNING)
            message.detail = f"Empty line in {str(line  + 1)}"
            message.line = str(line)
            messages.append(message)
            index_map[line] = ""
            continue
        index_string = tab[line][0]
        index_map[line] = index_string

        if (
            index_string not in model.INVESTIGATION_FILE_INITIAL_ROWS_SET
            and index_string not in model.INVESTIGATION_FILE_STUDY_ROWS_SET
        ):
            if index_string.startswith("#"):
                ignore_comments.append(line)
                messages.append(
                    ParserMessage(
                        type=ParserMessageType.INFO,
                        short="File comment line",
                        detail=f"Comment at line {str(line + 1)}:{index_string}",
                    )
                )
                continue
            if index_string.startswith("Comment"):
                if not is_study_part:
                    is_valid, message_detail = add_line_comment(
                        line, index_string, current_section, inital_part_comments, tab
                    )
                else:
                    is_valid, message_detail = add_line_comment(
                        line, index_string, current_section, study_part_comment, tab
                    )
                if not is_valid:
                    message = ParserMessage(
                        short="Invalid ISA comment line", type=ParserMessageType.WARNING
                    )
                    message.detail = f"{message_detail}"
                    message.line = str(line)
                    messages.append(message)
                continue
            else:
                message = ParserMessage(short="Invalid line", type=ParserMessageType.ERROR)
                message.detail = f" {index_string}"
                messages.append(message)
                message.line = str(line)
                continue

        if re.match(r"^[A-Z][A-Z0-9 ]+[A-Z0-9]$", index_string):
            current_section = index_string
            if index_string != "STUDY":
                continue

        if not current_section:
            message = ParserMessage(short="Invalid start section", type=ParserMessageType.ERROR)
            message.detail = f"Line {str(line + 1)}: {index_string} is not valid section start"
            messages.append(message)
            message.line = str(line)

        if not is_study_part:
            if index_string == "STUDY":
                is_study_part = True
            elif index_string not in model.INVESTIGATION_FILE_INITIAL_ROWS_SET:
                message = ParserMessage(
                    short="Unexpected line in the section", type=ParserMessageType.ERROR
                )
                message.detail = f"Unexpected line in {str(line  + 1)}"
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
                study_part_comment = {}
                study_parts_index_map.append(study_part_index)
                study_part_comment_list.append(study_part_comment)
                study_parts.append(study_part)

            if index_string not in model.INVESTIGATION_FILE_STUDY_ROWS_SET:
                message = ParserMessage(
                    short="Unexpected line in the study section",
                    type=ParserMessageType.ERROR,
                )
                message.detail = f"Unexpected line in {str(line  + 1)}"
                message.line = str(line)
                messages.append(message)
                continue
            if study_part or new_study_part:
                study_part.append(index_string)
                study_part_index[index_string] = line

    studies = build_studies(
        source,
        messages,
        study_parts,
        study_parts_index_map,
        study_part_comment_list,
        tab,
    )

    investigation, _ = build_investigation(
        source,
        initial_part_index_map,
        tab,
        studies,
        inital_part_comments,
        messages=messages,
    )
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
    study: model.Study = model.Study()
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
    studies: List[model.Study],
    comments_map: dict,
    messages: Union[None, List[ParserMessage]] = None,
):
    messages = messages if messages is not None else []
    investigation: model.Investigation = model.Investigation()
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
    data_schema = data.schema()
    if "properties" not in data_schema or not data_schema["properties"]:
        print(f"Properties are not defined in {file_path}")
        message = ParserMessage(
            short="Property is not defined for object", type=ParserMessageType.WARNING
        )
        message.detail = f"{data.__repr_name__} values will not assigned."
        messages.append(message)
        return

    initial_name_prefix = prefix or ""
    section_prefix = ""
    if hasattr(data, "section_prefix"):
        section_prefix = data.section_prefix.strip()
        initial_name_prefix = (
            section_prefix
            if not initial_name_prefix
            else f"{initial_name_prefix.strip()} {section_prefix}".strip()
        )
    if hasattr(data, "section_header") and hasattr(data, "comments") and comments_map:
        section_header = data.section_header or ""
        if section_header in comments_map and comments_map[section_header]:
            data.comments = []
            for comment in comments_map[section_header]:
                data.comments.append(Comment(name=comment[0], value=comment[1]))

    for key in data_schema["properties"]:
        field_name = ""
        data_type = "invalid"
        ref_object_definition = ""
        name_prefix = initial_name_prefix
        field_definition = data_schema["properties"][key]
        if (
            not field_definition
            or "auto_fill" not in field_definition
            or not field_definition["auto_fill"]
        ):
            continue
        if "inherit_prefix" in field_definition and not field_definition["inherit_prefix"]:
            name_prefix = prefix.strip() if prefix else ""

        if "$ref" in field_definition and field_definition["$ref"]:
            data_type = "ref"
            ref_object_definition = field_definition["$ref"]
        elif "allOf" in field_definition and field_definition["allOf"]:
            if "$ref" in field_definition["allOf"][0] and field_definition["allOf"][0]["$ref"]:
                data_type = "ref"
                ref_object_definition = field_definition["allOf"][0]["$ref"]
        elif "anyOf" in field_definition and field_definition["anyOf"]:
            primitives = {"string", "int", "float"}
            for field_item in field_definition["anyOf"]:
                if "type" in field_item and field_item["type"] in primitives:
                    data_type = "string"
                    break
        elif field_definition and "type" in field_definition:
            data_type = field_definition["type"]
        text_multiple_value = False
        if (
            field_definition
            and "text_multiple_value" in field_definition
            and field_definition["text_multiple_value"]
        ):
            text_multiple_value = True
        if field_definition and "header_name" in field_definition:
            if "section_prefix" in field_definition and field_definition["section_prefix"]:
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
                            if (
                                "section_prefix" in field_definition
                                and field_definition["section_prefix"]
                            ):
                                search_field = " ".join(
                                    [
                                        name_prefix,
                                        field_definition["section_prefix"],
                                        field_definition["search_header"],
                                    ]
                                )
                            else:
                                search_field = f"{name_prefix} {field_definition['search_header']}"

                        item_list = []
                        setattr(data, key, item_list)

                        if search_field not in index_map:
                            print(
                                f"{search_field} is not in file. Skipping {field_name} in {file_path}"
                            )
                            continue
                        index = index_map[search_field]

                        max = len(tab[index])
                        ref_class_name = (
                            items["$ref"].replace("#/definitions/", "").replace("#/$defs/", "")
                        )
                        ref_class = getattr(
                            sys.modules[model_module_name],
                            ref_class_name,
                        )
                        for i in range(1, max):
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
                            items["$ref"].replace("#/definitions/", "").replace("#/$defs/", "")
                        )
                        ref_class = getattr(
                            sys.modules[model_module_name],
                            ref_class_name,
                        )
                        instance = ref_class()
                        setattr(data, key, [instance])
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
                        item_schema = instance.schema()

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
                            item_val = getattr(instance, item_key) or ""
                            seperated_values = item_val.split(separator)
                            for _ in range(len(seperated_values)):
                                instance_count = len(new_instances)
                                values_count = len(seperated_values)
                                if instance_count < values_count:
                                    for _ in range(instance_count, values_count):
                                        new_instances.append(ref_class())
                                for j in range(values_count):
                                    setattr(new_instances[j], item_key, seperated_values[j])
                        count = len(new_instances)
                        for i in range(len(new_instances)):
                            instance_item = new_instances[count - i - 1]
                            if IsaAbstractModel.is_empty_model(model=instance_item):
                                new_instances.pop()
                            else:
                                break
                        setattr(data, key, new_instances)
                    else:
                        message = ParserMessage(
                            short="Reference item is not valid",
                            type=ParserMessageType.WARNING,
                        )
                        message.detail = f"Reference item is not valid {data_type} "
                        messages.append(message)
                        print("Reference item is not valid")
                else:
                    message = ParserMessage(
                        short="There is not item", type=ParserMessageType.WARNING
                    )
                    message.detail = "There is not item"
                    messages.append(message)
                    print("There is not item")
            elif data_type == "string":
                if field_name not in index_map:
                    message = ParserMessage(
                        short="Index is not defined", type=ParserMessageType.WARNING
                    )
                    message.detail = f"{field_name} is not in {file_path}. "
                    messages.append(message)
                    print(f"{field_name} is not in {file_path}. Skipping")
                    setattr(data, key, "")
                    continue
                index = index_map[field_name]
                value = ""
                if len(tab[index]) > value_index:
                    value = tab[index][value_index]
                else:
                    value = ""
                setattr(data, key, str(value) or "")
            elif data_type == "ref":
                ref_class_name = ref_object_definition.replace("#/definitions/", "").replace(
                    "#/$defs/", ""
                )
                ref_class = getattr(sys.modules[model_module_name], ref_class_name)
                instance = ref_class()
                setattr(data, key, instance)
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
                    message = ParserMessage(short="Invalid data type", type=ParserMessageType.ERROR)
                    message.detail = f"Invalid data type {data_type} in {file_path}"
                    messages.append(message)
                else:
                    message = ParserMessage(
                        short=f"Invalid data type in {file_path}",
                        type=ParserMessageType.ERROR,
                    )
                    message.detail = "Data type is not valid"
                    messages.append(message)
