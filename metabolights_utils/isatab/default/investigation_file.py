import logging
import os
import pathlib
import sys
from io import IOBase
from typing import List, Union

from pydantic import BaseModel
from pydantic.alias_generators import to_camel, to_snake

from metabolights_utils.isatab.default.base_isa_file import BaseIsaFile
from metabolights_utils.isatab.default.parser.investigation_parser import (
    get_investigation,
)
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights_utils.isatab.writer import InvestigationFileWriter
from metabolights_utils.models.isa.common import IsaAbstractModel
from metabolights_utils.models.isa.investigation_file import BaseSection, Investigation
from metabolights_utils.models.isa.investigation_file import (
    module_name as inv_module_name,
)
from metabolights_utils.models.parser.common import ParserMessage, ParserReport
from metabolights_utils.models.parser.enums import ParserMessageType
from metabolights_utils.utils.hash_utils import MetabolightsHashUtils as HashUtils

logger = logging.getLogger(__name__)


class InvestigationFileException(Exception):
    def __init__(self, message="") -> None:
        self.message = message


class DefaultInvestigationFileReader(InvestigationFileReader, BaseIsaFile):
    def __init__(self) -> None:
        super(BaseIsaFile, self).__init__()

    def read(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
        skip_parser_info_messages: bool = True,
    ) -> InvestigationFileReaderResult:
        buffer_or_path, path = self._get_file_path(file_buffer_or_path)
        investigation = Investigation()
        parse_success = False
        read_messages: List[ParserMessage] = []
        try:
            file_buffer = self._get_file_buffer(buffer_or_path)
            investigation = get_investigation(file_buffer, path, messages=read_messages)

            messages = read_messages
            parse_success = True
        except UnicodeDecodeError as err:
            logger.warning(
                "UnicodeDecodeError error. Trying with ascii encoding: %s", str(err)
            )
            try:
                read_messages.append(
                    ParserMessage(
                        type=ParserMessageType.WARNING,
                        short="UnicodeDecodeError error. Trying with ascii encoding.",
                        detail=(str(err)),
                    )
                )
                file_buffer = self._get_file_buffer(buffer_or_path, encoding="ascii")
                investigation = get_investigation(
                    file_buffer,
                    path,
                    messages=read_messages,
                )

                messages = read_messages
                parse_success = True
            except Exception as exc:
                logger.exception("File parse error: %s", str(exc))
                read_messages.append(
                    ParserMessage(
                        type=ParserMessageType.CRITICAL,
                        short="Parse error",
                        detail=(str(exc)),
                    )
                )
        except Exception as exc:
            logger.exception("File parse error: %s", str(exc))
            read_messages.append(
                ParserMessage(
                    type=ParserMessageType.CRITICAL,
                    short="Parse error",
                    detail=(str(exc)),
                )
            )
        finally:
            self._close_file(file_buffer_or_path)
        messages = read_messages if read_messages else []
        if skip_parser_info_messages:
            messages = [x for x in read_messages if x.type != ParserMessageType.INFO]
        report = ParserReport(messages=messages)

        result = InvestigationFileReaderResult(
            investigation=investigation, parser_report=report
        )

        if parse_success:
            logger.debug("File is parsed successfully.")
            if pathlib.Path(path).exists():
                result.sha256_hash = HashUtils.sha256sum(path)
                logger.debug("SHA256 of File %s: %s", path, result.sha256_hash)

            elif (
                isinstance(buffer_or_path, str)
                or isinstance(buffer_or_path, pathlib.Path)
            ) and pathlib.Path(str(buffer_or_path)).exists():
                result.sha256_hash = HashUtils.sha256sum(str(buffer_or_path))
                logger.debug(
                    "SHA256 of File %s: %s", str(buffer_or_path), result.sha256_hash
                )
        return result


class DefaultInvestigationFileWriter(InvestigationFileWriter, BaseIsaFile):
    def write(
        self,
        investigation: Investigation,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase, None] = None,
        values_in_quotation_mark: bool = False,
        verify_file_after_update: bool = True,
        skip_parser_info_messages: bool = True,
        investigation_module_name: Union[None, str] = None,
        sync_comments_from_fields: bool = True,
    ) -> InvestigationFileReaderResult:
        if sync_comments_from_fields:
            investigation.sync_comments_from_fields()

        content = InvestigationFileSerializer.to_isa_file_string(
            investigation=investigation,
            values_in_quotation_mark=values_in_quotation_mark,
            investigation_module_name=investigation_module_name,
        )
        file_path = None
        try:
            if isinstance(file_buffer_or_path, IOBase):
                parent_dir = os.path.dirname(os.path.realpath(file_buffer_or_path.name))
                os.makedirs(parent_dir, exist_ok=True)
                file_buffer_or_path.write(content)
                file_path = os.path.realpath(file_buffer_or_path.name)
            else:
                file_path = os.path.realpath(str(file_buffer_or_path))
                parent_dir = os.path.dirname(file_path)
                os.makedirs(parent_dir, exist_ok=True)
                with open(file_buffer_or_path, "w", encoding="utf-8") as f:
                    f.write(content)
            report = ParserReport()
            if verify_file_after_update:
                read_messages: List[ParserMessage] = []
                if isinstance(file_buffer_or_path, IOBase):
                    investigation = get_investigation(
                        file_buffer_or_path,
                        file_buffer_or_path.name,
                        messages=read_messages,
                    )
                else:
                    investigation = get_investigation(
                        None, file_buffer_or_path, messages=read_messages
                    )
                messages = read_messages
                if skip_parser_info_messages:
                    messages = [
                        x for x in read_messages if x.type != ParserMessageType.INFO
                    ]
                report = ParserReport(messages=messages)

                result = InvestigationFileReaderResult(
                    investigation=investigation,
                    parser_report=report,
                    file_path=str(file_path),
                )
            if os.path.exists(file_path):
                result.sha256_hash = HashUtils.sha256sum(file_path)

            return result
        except Exception as exc:
            raise exc


class InvestigationFileSerializer:
    @classmethod
    def to_isa_file_lines(
        cls,
        investigation: Investigation,
        values_in_quotation_mark: bool = False,
        investigation_module_name: Union[None, str] = None,
    ):
        module_name = (
            investigation_module_name if investigation_module_name else inv_module_name
        )
        file_lines = []
        for row in cls.to_isa_file_line_list(
            investigation,
            investigation_module_name=module_name,
        ):
            for i in range(len(row)):
                item = str(row[i]).strip('"')
                row[i] = f'"{item}"' if i > 0 and values_in_quotation_mark else item
            file_lines.append("\t".join(row))

        return file_lines

    @classmethod
    def to_isa_file_string(
        cls,
        investigation: Investigation,
        values_in_quotation_mark: bool = False,
        investigation_module_name: Union[None, str] = None,
    ):
        file_lines = cls.to_isa_file_lines(
            investigation,
            values_in_quotation_mark,
            investigation_module_name=investigation_module_name,
        )

        return "\n".join(file_lines) + "\n"

    @classmethod
    def to_isa_file_line_list(
        cls,
        investigation: Investigation,
        investigation_module_name: Union[None, str] = None,
    ):
        rows: List[List[str]] = []
        rows.extend(
            cls.add_sub_section(
                "",
                investigation.ontology_source_references,
                investigation_module_name=investigation_module_name,
            )
        )
        rows.extend(
            cls.add_sub_section(
                "",
                investigation,
                investigation_module_name=investigation_module_name,
            )
        )
        rows.extend(
            cls.add_sub_section(
                investigation.isatab_config.section_prefix,
                investigation.investigation_publications,
                investigation_module_name=investigation_module_name,
            )
        )
        rows.extend(
            cls.add_sub_section(
                investigation.isatab_config.section_prefix,
                investigation.investigation_contacts,
                investigation_module_name=investigation_module_name,
            )
        )
        for study in investigation.studies:
            rows.extend(
                cls.add_sub_section(
                    "",
                    study,
                    investigation_module_name=investigation_module_name,
                )
            )
            rows.extend(
                cls.add_sub_section(
                    study.isatab_config.section_prefix,
                    study.study_design_descriptors,
                    investigation_module_name=investigation_module_name,
                )
            )
            rows.extend(
                cls.add_sub_section(
                    study.isatab_config.section_prefix,
                    study.study_publications,
                    investigation_module_name=investigation_module_name,
                )
            )
            rows.extend(
                cls.add_sub_section(
                    study.isatab_config.section_prefix,
                    study.study_factors,
                    investigation_module_name=investigation_module_name,
                )
            )
            rows.extend(
                cls.add_sub_section(
                    study.isatab_config.section_prefix,
                    study.study_assays,
                    investigation_module_name=investigation_module_name,
                )
            )
            rows.extend(
                cls.add_sub_section(
                    study.isatab_config.section_prefix,
                    study.study_protocols,
                    investigation_module_name=investigation_module_name,
                )
            )
            rows.extend(
                cls.add_sub_section(
                    study.isatab_config.section_prefix,
                    study.study_contacts,
                    investigation_module_name=investigation_module_name,
                )
            )
        return rows

    @staticmethod
    def get_attribute(model, field_name):
        model_field_name = to_snake(field_name)
        return getattr(model, model_field_name)

    @classmethod
    def add_sub_section(
        cls,
        prefix,
        model: BaseSection,
        investigation_module_name: Union[None, str] = None,
    ):
        module_name = (
            investigation_module_name if investigation_module_name else inv_module_name
        )
        rows: List[List[str]] = [[model.isatab_config.section_header]]
        header = []
        if prefix:
            header.append(prefix)
        data_schema = model.model_json_schema()
        field_order = model.isatab_config.field_order
        if not field_order:
            field_order = []
        header_name = model.isatab_config.section_prefix
        if header_name:
            header.append(header_name)

        for field_name in field_order:
            value = cls.get_attribute(model, field_name)
            field_key = to_camel(field_name)
            if isinstance(value, list):
                properties = data_schema["properties"]
                if "allOf" in properties[field_key] or "items" in properties[field_key]:
                    if "allOf" in properties[field_key]:
                        item_ref = properties[field_key]["allOf"][0]["$ref"]
                    else:
                        item_ref = properties[field_key]["items"]["$ref"]
                    default_object_name = item_ref.replace(
                        "#/definitions/", ""
                    ).replace("#/$defs/", "")
                    obj = None
                    if module_name != inv_module_name:
                        try:
                            obj: BaseModel = getattr(
                                sys.modules[module_name],
                                default_object_name,
                            )
                        except:  # noqa: E722
                            pass
                    # not set a value try to find on default module
                    if not obj:
                        obj: BaseModel = getattr(
                            sys.modules[inv_module_name],
                            default_object_name,
                        )
                    props_base = obj.model_json_schema(by_alias=False)["properties"]
                    props = {to_camel(x): props_base[x] for x in props_base}
                    header.append(data_schema["properties"][field_key]["header_name"])
                    sub_model_rows = cls.add_model_content(
                        " ".join(header).strip(),
                        value,
                        props,
                        investigation_module_name=module_name,
                    )
                    if sub_model_rows:
                        rows.extend(sub_model_rows)
            elif isinstance(value, str):
                field_attribute = to_snake(field_name)
                header_name = model.__class__.model_fields[
                    field_attribute
                ].json_schema_extra["header_name"]
                header_name = (
                    f"{model.isatab_config.section_prefix} {header_name}"
                    if model.isatab_config.section_prefix
                    else header_name
                )
                rows.append([header_name, value])
            else:
                raise InvestigationFileException(
                    message=f"Unsupported type {type(value)}. Value {str(value)}"
                )

        cls.add_comments(model, rows)
        return rows

    @classmethod
    def add_comments(cls, model: BaseSection, rows: List[List[str]]):
        for comment in model.comments:
            comment_line = [f"Comment[{comment.name}]"]
            rows.append(comment_line)
            for value in comment.value:
                comment_line.append(value)

    @classmethod
    def add_model_content(
        cls,
        prefix,
        items: List[IsaAbstractModel],
        properties,
        investigation_module_name: Union[None, str] = None,
    ):
        module_name = (
            investigation_module_name if investigation_module_name else inv_module_name
        )
        rows = []
        row_map = {}
        fields = properties["isatabConfig"]["default"].get("fieldOrder")
        if not fields:
            fields = properties["isatabConfig"]["default"]["field_order"]
        for i in range(len(fields)):
            field = fields[i]
            field_key = to_camel(field)
            header_name = properties[field_key]["header_name"]
            header_name = f"{prefix} {header_name}".strip() if prefix else header_name
            if (
                "allOf" in properties[field_key]
                or "items" in properties[field_key]
                or "$ref" in properties[field_key]
            ):
                if "allOf" in properties[field_key]:
                    item_ref: str = properties[field_key]["allOf"][0]["$ref"]
                elif "$ref" in properties[field_key]:
                    item_ref: str = properties[field_key]["$ref"]
                else:
                    item_ref: str = properties[field_key]["items"]["$ref"]
                class_name = item_ref.replace("#/definitions/", "").replace(
                    "#/$defs/", ""
                )
                obj = None
                if module_name != inv_module_name:
                    try:
                        obj: BaseModel = getattr(
                            sys.modules[module_name],
                            class_name,
                        )
                    except:  # noqa: E722
                        pass
                # not set a value try to find on default module
                if not obj:
                    obj: BaseModel = getattr(
                        sys.modules[inv_module_name],
                        class_name,
                    )
                props_base = obj.model_json_schema(by_alias=False)["properties"]
                props = {to_camel(x): props_base[x] for x in props_base}
                input_items = (
                    [cls.get_attribute(item, field_key) for item in items]
                    if items
                    else [obj()]
                )
                item_values = cls.add_model_content(
                    header_name,
                    input_items,
                    props,
                    investigation_module_name=module_name,
                )
                rows.extend(item_values)
            elif "type" in properties[field_key]:
                cls.assign_type(
                    items, properties, rows, row_map, fields, i, header_name
                )
            elif "anyOf" in properties[field_key]:
                cls.assign_string_type(items, rows, row_map, fields, i, header_name)
            else:
                logger.error(
                    "Unsupported type %s for prefix %s", properties[field_key], prefix
                )
        return rows

    @classmethod
    def assign_type(cls, items, properties, rows, row_map, fields, i, header_name):
        field_key = to_camel(fields[i])
        object_type = properties[field_key]["type"]
        if object_type == "string":
            row_map[header_name] = [header_name]
            rows.append(row_map[header_name])
            if items:
                for item in items:
                    if isinstance(item, list):
                        sub_items = []
                        if item:
                            for sub_item in item:
                                sub_items.append(cls.get_attribute(sub_item, field_key))
                        else:
                            sub_items.append("")
                        row_map[header_name].append(";".join(sub_items))
                    else:
                        value = cls.get_attribute(item, field_key)
                        row_map[header_name].append(value)
            else:
                row_map[header_name].append("")
        else:
            raise InvestigationFileException(
                message=f"Invalid object type {object_type}"
            )

    @classmethod
    def assign_string_type(cls, items, rows, row_map, fields, i, header_name):
        field_key = to_camel(fields[i])
        row_map[header_name] = [header_name]
        rows.append(row_map[header_name])
        if items:
            for item in items:
                if isinstance(item, list):
                    sub_items = []
                    if item:
                        for sub_item in item:
                            sub_items.append(
                                str(cls.get_attribute(sub_item, field_key))
                            )
                    else:
                        sub_items.append("")
                    row_map[header_name].append(";".join(sub_items))
                else:
                    value = str(cls.get_attribute(item, field_key))
                    row_map[header_name].append(value)
        else:
            row_map[header_name].append("")
