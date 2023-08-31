from typing import Dict, List, Union

import humps
from pydantic import BaseModel, Extra, Field

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.isa.enums import ColumnsStructure
from metabolights_utils.tsv.filter import TsvFileFilterOption
from metabolights_utils.tsv.sort import TsvFileSortOption

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


class IsaAbstractModel(MetabolightsBaseModel):
    field_order: Union[None, List[str]] = Field(None, auto_fill=False)

    class Config:
        extra = Extra.forbid

    @classmethod
    def get_attribute(cls, model: BaseModel, attribute_name):
        model_attribute_key = humps.decamelize(attribute_name)
        return getattr(model, model_attribute_key)

    @classmethod
    def is_empty_model(cls, model: BaseModel):
        schema = model.schema()
        for item_key in schema["properties"]:
            item_field_definition = schema["properties"][item_key]
            if (
                not item_field_definition
                or "auto_fill" not in item_field_definition
                or not item_field_definition["auto_fill"]
            ):
                continue
            model_attribute_key = humps.decamelize(item_key)
            item_val = cls.get_attribute(model, model_attribute_key)
            if isinstance(item_val, IsaAbstractModel):
                is_empty = IsaAbstractModel.is_empty_model(item_val)
                if not is_empty:
                    return False
            elif item_val:
                return False
        return True


class AssayTechnique(IsaAbstractModel):
    name: str = ""
    main_technique: str = ""
    technique: str = ""
    sub_technique: str = ""

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return self.__str__()


class OntologyItem(IsaAbstractModel):
    term: str = ""
    term_source_ref: str = ""
    term_accession_number: str = ""

    def __str__(self) -> str:
        if self.term:
            if self.term_source_ref or self.term_accession_number:
                return (
                    f"{self.term} [{self.term_source_ref}:{self.term_accession_number}]"
                )
            else:
                return self.term
        return ""

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return self.__str__()


class OrganismAndOrganismPartPair(IsaAbstractModel):
    organism: OntologyItem = OntologyItem()
    organism_part: OntologyItem = OntologyItem()
    variant: OntologyItem = OntologyItem()
    sample_type: OntologyItem = OntologyItem()

    def __str__(self) -> str:
        if self.organism and self.organism_part and self.variant and self.sample_type:
            return ":".join(
                [
                    self.organism.__str__(),
                    self.organism_part.__str__(),
                    self.variant.__str__(),
                    self.sample_type.__str__(),
                ]
            )

        if self.organism and self.organism_part and self.variant:
            return ":".join(
                [
                    self.organism.__str__(),
                    self.organism_part.__str__(),
                    self.variant.__str__(),
                ]
            )
        if self.organism and self.organism_part:
            return ":".join([self.organism.__str__(), self.organism_part.__str__()])
        if self.organism:
            return self.organism.__str__()

        return ""

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return self.__str__()


class NumericItem(OntologyItem):
    value: str = ""
    unit: OntologyItem = OntologyItem()


class ProtocolField(MetabolightsBaseModel):
    header_name: str = ""


class ProtocolOntologyItem(ProtocolField):
    data: List[OntologyItem] = []


class ProtocolTextItem(ProtocolField):
    data: List[str] = []


class ProtocolNumericOntologyItem(ProtocolField):
    data: List[NumericItem] = []


class ProtocolItem(MetabolightsBaseModel):
    name: str = ""
    text_fields: Dict[str, ProtocolTextItem] = {}
    numeric_fields: Dict[str, ProtocolNumericOntologyItem] = {}
    ontology_fields: Dict[str, ProtocolOntologyItem] = {}


class ProtocolFields(MetabolightsBaseModel):
    name: str = ""
    text_fields: Dict[str, ProtocolTextItem] = {}
    numeric_fields: Dict[str, ProtocolNumericOntologyItem] = {}
    ontology_fields: Dict[str, ProtocolOntologyItem] = {}

    additional_text_fields: List[ProtocolTextItem] = []
    additional_numeric_fields: List[ProtocolNumericOntologyItem] = []
    additional_ontology_fields: List[ProtocolOntologyItem] = []


class Comment(IsaAbstractModel):
    name: str = ""
    value: List[str] = []


class IsaTableColumn(IsaAbstractModel):
    column_index: Union[int, str] = ""
    column_name: str = ""
    column_header: str = ""
    additional_columns: List[str] = []
    column_category: str = ""
    colummn_structure: ColumnsStructure = ColumnsStructure.SINGLE_COLUMN
    column_prefix: str = ""
    column_search_pattern: str = ""

    def __hash__(self):
        return hash(self.column_name)


class IsaTable(IsaAbstractModel):
    columns: List[str] = Field([])
    headers: List[IsaTableColumn] = Field([])
    data: Dict[str, List[str]] = Field({})
    row_indices: List[int] = []
    column_indices: List[int] = []
    filtered_total_row_count: int = 0
    row_offset: int = 0
    row_count: int = 0
    total_row_count: int = 0
    selected_column_count: int = 0
    total_column_count: int = 0
    filter_options: List[TsvFileFilterOption] = []
    sort_options: List[TsvFileSortOption] = []


class IsaTableFile(IsaAbstractModel):
    file_path: str = ""
    table: IsaTable = Field(IsaTable())
