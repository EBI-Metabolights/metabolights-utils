import sys
from typing import List

from pydantic import Field

from metabolights_utils.models.isa.common import Comment, IsaAbstractModel


class BaseSection(IsaAbstractModel):
    section_header: str = Field("ONTOLOGY SOURCE REFERENCE", exclude=True)
    section_prefix: str = Field("", exclude=True)

    comments: List[Comment] = []

    class Config:
        field_order: List[str] = []


class OntologySourceReference(IsaAbstractModel):
    field_order: List[str] = [
        "sourceName",
        "sourceFile",
        "sourceVersion",
        "sourceDescription",
    ]
    sourceName: str = Field("", sourceDescription=True, auto_fill=True, header_name="Source Name")
    sourceFile: str = Field("", auto_fill=True, header_name="Source File")
    sourceVersion: str = Field("", auto_fill=True, header_name="Source Version")
    sourceDescription: str = Field("", auto_fill=True, header_name="Source Description")


class OntologyAnnotation(IsaAbstractModel):
    field_order: List[str] = ["term", "termAccessionNumber", "termSourceRef"]

    term: str = Field("", auto_fill=True, header_name="")
    termAccessionNumber: str = Field("", auto_fill=True, header_name="Term Accession Number")
    termSourceRef: str = Field("", auto_fill=True, header_name="Term Source REF")


class ValueTypeAnnotation(IsaAbstractModel):
    field_order: List[str] = ["name", "type", "termAccessionNumber", "termSourceRef"]
    name: str = Field("", auto_fill=True, header_name="Name")
    type: str = Field("", auto_fill=True, header_name="Type")
    termAccessionNumber: str = Field("", auto_fill=True, header_name="Type Term Accession Number")
    termSourceRef: str = Field("", auto_fill=True, header_name="Type Term Source REF")


class Publication(IsaAbstractModel):
    field_order: List[str] = ["pubMedID", "doi", "authorList", "title", "status"]

    pubMedID: str = Field("", auto_fill=True, header_name="PubMed ID")
    doi: str = Field("", auto_fill=True, header_name="Publication DOI")
    authorList: str = Field("", auto_fill=True, header_name="Publication Author List")
    title: str = Field("", auto_fill=True, header_name="Publication Title")
    status: OntologyAnnotation = Field(
        OntologyAnnotation(), auto_fill=True, header_name="Publication Status"
    )


class Person(IsaAbstractModel):
    field_order: List[str] = [
        "lastName",
        "firstName",
        "midInitials",
        "email",
        "phone",
        "fax",
        "address",
        "affiliation",
        "roles",
    ]
    lastName: str = Field("", auto_fill=True, header_name="Last Name")
    firstName: str = Field("", auto_fill=True, header_name="First Name")
    midInitials: str = Field("", auto_fill=True, header_name="Mid Initials")
    email: str = Field("", auto_fill=True, header_name="Email")
    phone: str = Field("", auto_fill=True, header_name="Phone")
    fax: str = Field("", auto_fill=True, header_name="Fax")
    address: str = Field("", auto_fill=True, header_name="Address")
    affiliation: str = Field("", auto_fill=True, header_name="Affiliation")
    roles: List[OntologyAnnotation] = Field(
        [],
        auto_fill=True,
        header_name="Roles",
        text_multiple_value=True,
        seperator=";",
    )


class Factor(IsaAbstractModel):
    field_order: List[str] = ["name", "type"]
    name: str = Field("", auto_fill=True, header_name="Name")
    type: OntologyAnnotation = Field(OntologyAnnotation(), auto_fill=True, header_name="Type")


class Assay(IsaAbstractModel):
    field_order: List[str] = [
        "fileName",
        "measurementType",
        "technologyType",
        "technologyPlatform",
    ]
    fileName: str = Field("", auto_fill=True, header_name="File Name")
    measurementType: OntologyAnnotation = Field(
        OntologyAnnotation(), auto_fill=True, header_name="Measurement Type"
    )
    technologyType: OntologyAnnotation = Field(
        OntologyAnnotation(), auto_fill=True, header_name="Technology Type"
    )
    technologyPlatform: str = Field("", auto_fill=True, header_name="Technology Platform")


class Protocol(IsaAbstractModel):
    field_order: List[str] = [
        "name",
        "protocolType",
        "description",
        "uri",
        "version",
        "parameters",
        "components",
    ]
    name: str = Field("", auto_fill=True, header_name="Name")
    protocolType: OntologyAnnotation = Field(
        OntologyAnnotation(), auto_fill=True, header_name="Type"
    )
    description: str = Field("", auto_fill=True, header_name="Description")
    uri: str = Field("", auto_fill=True, header_name="URI")
    version: str = Field("", auto_fill=True, header_name="Version")
    parameters: List[OntologyAnnotation] = Field(
        [],
        auto_fill=True,
        header_name="Parameters Name",
        text_multiple_value=True,
        seperator=";",
    )
    components: List[ValueTypeAnnotation] = Field(
        [],
        auto_fill=True,
        header_name="Components",
        text_multiple_value=True,
        seperator=";",
    )


######################################################################################################
# ISA TAB FILE SECTIONS
######################################################################################################


class OntologySourceReferences(BaseSection):
    field_order: List[str] = ["references"]

    section_header: str = Field("ONTOLOGY SOURCE REFERENCE", exclude=True)
    section_prefix: str = Field("Term", exclude=True)
    references: List[OntologySourceReference] = Field(
        [], auto_fill=True, header_name="", search_header="Source Name"
    )


class InvestigationPublications(BaseSection):
    section_header: str = Field("INVESTIGATION PUBLICATIONS", exclude=True)
    section_prefix: str = Field("", exclude=True)
    field_order: List[str] = ["publications"]
    publications: List[Publication] = Field(
        [], auto_fill=True, header_name="", search_header="Publication Title"
    )


class InvestigationContacts(BaseSection):
    section_header: str = Field("INVESTIGATION CONTACTS", exclude=True)
    section_prefix: str = Field("Person", exclude=True)

    field_order: List[str] = ["people"]
    people: List[Person] = Field([], auto_fill=True, header_name="", search_header="Last Name")


class StudyDesignDescriptors(BaseSection):
    field_order: List[str] = ["designTypes"]
    section_header: str = Field("STUDY DESIGN DESCRIPTORS", exclude=True)
    section_prefix: str = Field("Design", exclude=True)
    designTypes: List[OntologyAnnotation] = Field([], auto_fill=True, header_name="Type")


class StudyPublications(BaseSection):
    field_order: List[str] = ["publications"]
    section_header: str = Field("STUDY PUBLICATIONS", exclude=True)
    section_prefix: str = Field("", exclude=True)
    publications: List[Publication] = Field(
        [], auto_fill=True, header_name="", search_header="Publication Title"
    )


class StudyFactors(BaseSection):
    field_order: List[str] = ["factors"]
    section_header: str = Field("STUDY FACTORS", exclude=True)
    section_prefix: str = Field("Factor", exclude=True)
    factors: List[Factor] = Field([], auto_fill=True, header_name="", search_header="Name")


class StudyAssays(BaseSection):
    field_order: List[str] = ["assays"]
    section_header: str = Field("STUDY ASSAYS", exclude=True)
    section_prefix: str = Field("Assay", exclude=True)
    assays: List[Assay] = Field([], auto_fill=True, header_name="", search_header="File Name")


class StudyProtocols(BaseSection):
    field_order: List[str] = ["protocols"]
    section_header: str = Field("STUDY PROTOCOLS", exclude=True)
    section_prefix: str = Field("Protocol", exclude=True)
    protocols: List[Protocol] = Field([], auto_fill=True, header_name="", search_header="Name")


class StudyContacts(BaseSection):
    field_order: List[str] = ["people"]
    section_header: str = Field("STUDY CONTACTS", exclude=True)
    section_prefix: str = Field("Person", exclude=True)
    people: List[Person] = Field([], auto_fill=True, header_name="", search_header="Last Name")


class Study(BaseSection):
    field_order: List[str] = [
        "identifier",
        "title",
        "description",
        "submissionDate",
        "publicReleaseDate",
        "fileName",
    ]
    section_header: str = Field("STUDY", exclude=True)
    section_prefix: str = Field("Study", exclude=True)
    identifier: str = Field("", auto_fill=True, header_name="Identifier")
    title: str = Field("", auto_fill=True, header_name="Title")
    description: str = Field("", auto_fill=True, header_name="Description")
    submissionDate: str = Field("", auto_fill=True, header_name="Submission Date")
    publicReleaseDate: str = Field("", auto_fill=True, header_name="Public Release Date")
    fileName: str = Field("", auto_fill=True, header_name="File Name")

    studyDesignDescriptors: StudyDesignDescriptors = Field(
        StudyDesignDescriptors(), auto_fill=True, header_name=""
    )
    studyPublications: StudyPublications = Field(
        StudyPublications(), auto_fill=True, header_name=""
    )
    studyFactors: StudyFactors = Field(StudyFactors(), auto_fill=True, header_name="")
    studyAssays: StudyAssays = Field(StudyAssays(), auto_fill=True, header_name="")
    studyProtocols: StudyProtocols = Field(StudyProtocols(), auto_fill=True, header_name="")
    studyContacts: StudyContacts = Field(StudyContacts(), auto_fill=True, header_name="")


class Investigation(BaseSection):
    section_header: str = Field("INVESTIGATION", exclude=True)
    section_prefix: str = Field("Investigation", exclude=True)
    field_order: List[str] = [
        "identifier",
        "title",
        "description",
        "submissionDate",
        "publicReleaseDate",
    ]
    specificationVersion: str = Field("1.0")
    specificationDate: str = Field("2016-10-28")

    identifier: str = Field("", auto_fill=True, header_name="Identifier")
    title: str = Field("", auto_fill=True, header_name="Title")
    description: str = Field("", auto_fill=True, header_name="Description")
    submissionDate: str = Field("", auto_fill=True, header_name="Submission Date")
    publicReleaseDate: str = Field("", auto_fill=True, header_name="Public Release Date")

    ontologySourceReferences: OntologySourceReferences = Field(
        OntologySourceReferences(), auto_fill=True, header_name="", inherit_prefix=False
    )
    investigationPublications: InvestigationPublications = Field(
        InvestigationPublications(), auto_fill=True, header_name=""
    )
    investigationContacts: InvestigationContacts = Field(
        InvestigationContacts(), auto_fill=True, header_name=""
    )
    studies: List[Study] = []

    def to_isa_file_lines(self, values_in_quatation_mark: bool = False):
        file_lines = []
        for row in self.to_isa_file_list():
            for i in range(len(row)):
                item = row[i].strip('"')
                row[i] = f'"{item}"' if i > 0 and values_in_quatation_mark else item
            file_lines.append("\t".join(row))

        return file_lines

    def to_isa_file_string(self, values_in_quatation_mark: bool = False):
        file_lines = self.to_isa_file_lines(values_in_quatation_mark)

        return "\n".join(file_lines) + "\n"

    def to_isa_file_list(self):
        rows: List[List[str]] = []
        rows.extend(self.add_sub_section("", self.ontologySourceReferences))
        rows.extend(self.add_sub_section("", self))
        rows.extend(self.add_sub_section(self.section_prefix, self.investigationPublications))
        rows.extend(self.add_sub_section(self.section_prefix, self.investigationContacts))
        for study in self.studies:
            rows.extend(self.add_sub_section("", study))
            rows.extend(self.add_sub_section(study.section_prefix, study.studyDesignDescriptors))
            rows.extend(self.add_sub_section(study.section_prefix, study.studyPublications))
            rows.extend(self.add_sub_section(study.section_prefix, study.studyFactors))
            rows.extend(self.add_sub_section(study.section_prefix, study.studyAssays))
            rows.extend(self.add_sub_section(study.section_prefix, study.studyProtocols))
            rows.extend(self.add_sub_section(study.section_prefix, study.studyContacts))
        return rows

    def add_sub_section(self, prefix, model: BaseSection):
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
                    obj = getattr(sys.modules[__name__], default_object_name)
                    props = obj.schema()["properties"]
                    header.append(data_schema["properties"][field_name]["header_name"])
                    sub_model_rows = self.add_model_content(" ".join(header).strip(), value, props)
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

        self.add_comments(model, rows)
        return rows

    def add_comments(self, model: BaseSection, rows: List[List[str]]):
        for comment in model.comments:
            comment_line = [f"Comment[{comment.name}]"]
            rows.append(comment_line)
            for value in comment.value:
                comment_line.append(value)

    def add_model_content(self, prefix, items: List[IsaAbstractModel], properties):
        rows = []
        row_map = {}
        fields = properties["field_order"]["default"]
        for i in range(len(fields)):
            header_name = properties[fields[i]]["header_name"]
            header_name = f"{prefix} {header_name}".strip() if prefix else header_name
            if "allOf" in properties[fields[i]] or "items" in properties[fields[i]]:
                if "allOf" in "allOf" in properties[fields[i]]:
                    item_ref = properties[fields[i]]["allOf"][0]["$ref"]
                else:
                    item_ref = properties[fields[i]]["items"]["$ref"]
                class_name = item_ref.replace("#/definitions/", "").replace("#/$defs/", "")
                obj = getattr(sys.modules[__name__], class_name)
                props = obj.schema()["properties"]
                input_items = [getattr(item, fields[i]) for item in items] if items else [obj()]

                item_values = self.add_model_content(header_name, input_items, props)
                rows.extend(item_values)
            elif "type" in properties[fields[i]]:
                self.assign_type(items, properties, rows, row_map, fields, i, header_name)

        return rows

    def assign_type(self, items, properties, rows, row_map, fields, i, header_name):
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


INVESTIGATION_FILE_INITIAL_ROWS = [
    "ONTOLOGY SOURCE REFERENCE",
    "Term Source Name",
    "Term Source File",
    "Term Source Version",
    "Term Source Description",
    "INVESTIGATION",
    "Investigation Identifier",
    "Investigation Title",
    "Investigation Description",
    "Investigation Submission Date",
    "Investigation Public Release Date",
    "INVESTIGATION PUBLICATIONS",
    "Investigation PubMed ID",
    "Investigation Publication DOI",
    "Investigation Publication Author List",
    "Investigation Publication Title",
    "Investigation Publication Status",
    "Investigation Publication Status Term Accession Number",
    "Investigation Publication Status Term Source REF",
    "INVESTIGATION CONTACTS",
    "Investigation Person Last Name",
    "Investigation Person First Name",
    "Investigation Person Mid Initials",
    "Investigation Person Email",
    "Investigation Person Phone",
    "Investigation Person Fax",
    "Investigation Person Address",
    "Investigation Person Affiliation",
    "Investigation Person Roles",
    "Investigation Person Roles Term Accession Number",
    "Investigation Person Roles Term Source REF",
]

INVESTIGATION_FILE_STUDY_ROWS = [
    "STUDY",
    "Study Identifier",
    "Study Title",
    "Study Description",
    "Study Submission Date",
    "Study Public Release Date",
    "Study File Name",
    "STUDY DESIGN DESCRIPTORS",
    "Study Design Type",
    "Study Design Type Term Accession Number",
    "Study Design Type Term Source REF",
    "STUDY PUBLICATIONS",
    "Study PubMed ID",
    "Study Publication DOI",
    "Study Publication Author List",
    "Study Publication Title",
    "Study Publication Status",
    "Study Publication Status Term Accession Number",
    "Study Publication Status Term Source REF",
    "STUDY FACTORS",
    "Study Factor Name",
    "Study Factor Type",
    "Study Factor Type Term Accession Number",
    "Study Factor Type Term Source REF",
    "STUDY ASSAYS",
    "Study Assay File Name",
    "Study Assay Measurement Type",
    "Study Assay Measurement Type Term Accession Number",
    "Study Assay Measurement Type Term Source REF",
    "Study Assay Technology Type",
    "Study Assay Technology Type Term Accession Number",
    "Study Assay Technology Type Term Source REF",
    "Study Assay Technology Platform",
    "STUDY PROTOCOLS",
    "Study Protocol Name",
    "Study Protocol Type",
    "Study Protocol Type Term Accession Number",
    "Study Protocol Type Term Source REF",
    "Study Protocol Description",
    "Study Protocol URI",
    "Study Protocol Version",
    "Study Protocol Parameters Name",
    "Study Protocol Parameters Name Term Accession Number",
    "Study Protocol Parameters Name Term Source REF",
    "Study Protocol Components Name",
    "Study Protocol Components Type",
    "Study Protocol Components Type Term Accession Number",
    "Study Protocol Components Type Term Source REF",
    "STUDY CONTACTS",
    "Study Person Last Name",
    "Study Person First Name",
    "Study Person Mid Initials",
    "Study Person Email",
    "Study Person Phone",
    "Study Person Fax",
    "Study Person Address",
    "Study Person Affiliation",
    "Study Person Roles",
    "Study Person Roles Term Accession Number",
    "Study Person Roles Term Source REF",
]

INVESTIGATION_FILE_INITIAL_ROWS_SET = set(INVESTIGATION_FILE_INITIAL_ROWS)
INVESTIGATION_FILE_STUDY_ROWS_SET = set(INVESTIGATION_FILE_STUDY_ROWS)
