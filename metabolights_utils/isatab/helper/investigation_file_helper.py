import pathlib
import sys
from abc import ABC
from io import IOBase
from typing import List, Tuple, Union

from pydantic import BaseModel, Field

from metabolights_utils.isatab.helper.base_isa_file_helper import BaseIsaFile
from metabolights_utils.isatab.investigation_file_reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights_utils.isatab.investigation_file_writer import InvestigationFileWriter
from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.isa.common import IsaAbstractModel
from metabolights_utils.models.isa.investigation_file import BaseSection, Investigation
from metabolights_utils.models.isa.investigation_file import module_name as inv_module_name
from metabolights_utils.models.isa.parser.investigation_parser import get_investigation
from metabolights_utils.models.parser.common import ParserMessage, ParserReport
from metabolights_utils.models.parser.enums import ParserMessageType


class InvestigationFileHelper(InvestigationFileWriter, InvestigationFileReader, BaseIsaFile):
    def read(
        self,
        file_buffer: IOBase = None,
        file_path: Union[str, pathlib.Path] = None,
        skip_parser_info_messages: bool = True,
    ) -> InvestigationFileReaderResult:
        buffer_or_path, path = self._get_file_buffer_and_path(file_buffer, file_path)
        file_buffer = self._get_file_buffer(buffer_or_path)
        try:
            read_messages: List[ParserMessage] = []
            investigation = get_investigation(file_buffer, path, messages=read_messages)
            messages = read_messages
            if skip_parser_info_messages:
                messages = [x for x in read_messages if x.type != ParserMessageType.INFO]
            report = ParserReport(messages=messages)
            return InvestigationFileReaderResult(investigation=investigation, parser_report=report)
        except Exception as exc:
            raise exc
        finally:
            self._close_file(file_buffer, file_path)

    def write(
        self,
        investigation: Investigation,
        file_buffer: IOBase = None,
        file_path: Union[str, pathlib.Path] = None,
        values_in_quatation_mark: bool = True,
        verify_file_after_update: bool = True,
        skip_parser_info_messages: bool = True,
    ) -> InvestigationFileReaderResult:
        content = InvestigationFileSerializer.to_isa_file_string(
            investigation=investigation, values_in_quatation_mark=values_in_quatation_mark
        )
        buffer_or_path, path = self._get_file_buffer_and_path(file_buffer, file_path)
        try:
            if file_buffer:
                file_buffer.write(content)
            else:
                with open(buffer_or_path, "w") as f:
                    f.write(content)

            if verify_file_after_update:
                read_messages: List[ParserMessage] = []
                new_investigation = get_investigation(buffer_or_path, path, messages=read_messages)
                messages = read_messages
                if skip_parser_info_messages:
                    messages = [x for x in read_messages if x.type != ParserMessageType.INFO]
                report = ParserReport(messages=messages)
                return InvestigationFileReaderResult(
                    investigation=new_investigation, parser_report=report
                )
            return InvestigationFileReaderResult(
                investigation=investigation, parser_report=ParserReport()
            )
        except Exception as exc:
            raise exc


class InvestigationFileSerializer(object):
    @classmethod
    def to_isa_file_lines(
        cls, investigation: Investigation, values_in_quatation_mark: bool = False
    ):
        file_lines = []
        for row in cls.to_isa_file_line_list(investigation):
            for i in range(len(row)):
                item = row[i].strip('"')
                row[i] = f'"{item}"' if i > 0 and values_in_quatation_mark else item
            file_lines.append("\t".join(row))

        return file_lines

    @classmethod
    def to_isa_file_string(
        cls, investigation: Investigation, values_in_quatation_mark: bool = False
    ):
        file_lines = cls.to_isa_file_lines(investigation, values_in_quatation_mark)

        return "\n".join(file_lines) + "\n"

    @classmethod
    def to_isa_file_line_list(cls, investigation: Investigation):
        rows: List[List[str]] = []
        rows.extend(cls.add_sub_section("", investigation.ontologySourceReferences))
        rows.extend(cls.add_sub_section("", investigation))
        rows.extend(
            cls.add_sub_section(
                investigation.section_prefix, investigation.investigationPublications
            )
        )
        rows.extend(
            cls.add_sub_section(investigation.section_prefix, investigation.investigationContacts)
        )
        for study in investigation.studies:
            rows.extend(cls.add_sub_section("", study))
            rows.extend(cls.add_sub_section(study.section_prefix, study.studyDesignDescriptors))
            rows.extend(cls.add_sub_section(study.section_prefix, study.studyPublications))
            rows.extend(cls.add_sub_section(study.section_prefix, study.studyFactors))
            rows.extend(cls.add_sub_section(study.section_prefix, study.studyAssays))
            rows.extend(cls.add_sub_section(study.section_prefix, study.studyProtocols))
            rows.extend(cls.add_sub_section(study.section_prefix, study.studyContacts))
        return rows

    @classmethod
    def add_sub_section(cls, prefix, model: BaseSection):
        rows: List[List[str]] = [[model.section_header]]
        header = []
        if prefix:
            header.append(prefix)
        data_schema = model.schema()
        field_order = model.field_order
        if not field_order:
            field_order = []
        header_name = model.section_prefix
        if header_name:
            header.append(header_name)

        for field_name in field_order:
            value = getattr(model, field_name)

            if isinstance(value, list):
                properties = data_schema["properties"]
                if "allOf" in properties[field_name] or "items" in properties[field_name]:
                    if "allOf" in "allOf" in properties[field_name]:
                        item_ref = properties[field_name]["allOf"][0]["$ref"]
                    else:
                        item_ref = properties[field_name]["items"]["$ref"]
                    default_object_name = item_ref.replace("#/definitions/", "").replace(
                        "#/$defs/", ""
                    )
                    obj = getattr(sys.modules[inv_module_name], default_object_name)
                    props = obj.schema()["properties"]
                    header.append(data_schema["properties"][field_name]["header_name"])
                    sub_model_rows = cls.add_model_content(" ".join(header).strip(), value, props)
                    if sub_model_rows:
                        rows.extend(sub_model_rows)
            elif isinstance(value, str):
                header_name = model.__fields__[field_name].field_info.extra["header_name"]
                header_name = (
                    f"{model.section_prefix} {header_name}" if model.section_prefix else header_name
                )
                rows.append([header_name, value])
            else:
                raise Exception()

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
    def add_model_content(cls, prefix, items: List[IsaAbstractModel], properties):
        rows = []
        row_map = {}
        fields = properties["field_order"]["default"]
        for i in range(len(fields)):
            header_name = properties[fields[i]]["header_name"]
            header_name = f"{prefix} {header_name}".strip() if prefix else header_name
            if "allOf" in properties[fields[i]] or "items" in properties[fields[i]]:
                if "allOf" in "allOf" in properties[fields[i]]:
                    item_ref: str = properties[fields[i]]["allOf"][0]["$ref"]
                else:
                    item_ref: str = properties[fields[i]]["items"]["$ref"]
                class_name = item_ref.replace("#/definitions/", "").replace("#/$defs/", "")
                obj: BaseModel = getattr(sys.modules[inv_module_name], class_name)
                props = obj.schema()["properties"]
                input_items = [getattr(item, fields[i]) for item in items] if items else [obj()]

                item_values = cls.add_model_content(header_name, input_items, props)
                rows.extend(item_values)
            elif "type" in properties[fields[i]]:
                cls.assign_type(items, properties, rows, row_map, fields, i, header_name)

        return rows

    @classmethod
    def assign_type(cls, items, properties, rows, row_map, fields, i, header_name):
        object_type = properties[fields[i]]["type"]
        if object_type == "string":
            row_map[header_name] = [header_name]
            rows.append(row_map[header_name])
            if items:
                for item in items:
                    if isinstance(item, list):
                        sub_items = []
                        if item:
                            for sub_item in item:
                                sub_items.append(getattr(sub_item, fields[i]))
                        else:
                            sub_items.append("")
                        row_map[header_name].append(";".join(sub_items))
                    else:
                        value = getattr(item, fields[i])
                        row_map[header_name].append(value)
            else:
                row_map[header_name].append("")
        else:
            raise Exception()
