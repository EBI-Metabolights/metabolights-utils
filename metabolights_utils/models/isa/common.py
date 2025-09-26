from typing import Dict, List, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_snake
from typing_extensions import Annotated

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.isa.enums import ColumnsStructure
from metabolights_utils.tsv.filter import TsvFileFilterOption
from metabolights_utils.tsv.sort import TsvFileSortOption

INVESTIGATION_FILE_SECTION_NAMES = {
    "ONTOLOGY SOURCE REFERENCE",
    "INVESTIGATION",
    "INVESTIGATION PUBLICATIONS",
    "INVESTIGATION CONTACTS",
    "STUDY",
    "STUDY DESIGN DESCRIPTORS",
    "STUDY PUBLICATIONS",
    "STUDY FACTORS",
    "STUDY ASSAYS",
    "STUDY PROTOCOLS",
    "STUDY CONTACTS",
}

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


class IsaTabConfig(MetabolightsBaseModel):
    field_order: Annotated[Union[None, List[str]], Field(description="")] = None
    section_header: Annotated[Union[None, str], Field(description="")] = None
    section_prefix: Annotated[Union[None, str], Field(description="")] = None
    specification_version: Annotated[str, Field(description="")] = ""
    specification_date: Annotated[str, Field(description="")] = ""


class IsaAbstractModel(MetabolightsBaseModel):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(exclude=True),
    ] = IsaTabConfig()
    # id: Annotated[Union[None, str], Field(alias="@id", default=None)] = None
    model_config = ConfigDict(extra="forbid")

    @classmethod
    def get_attribute(cls, model: BaseModel, attribute_name):
        model_attribute_key = to_snake(attribute_name)
        return getattr(model, model_attribute_key)

    @classmethod
    def is_empty_model(cls, model: BaseModel):
        schema = model.model_json_schema()
        for item_key in schema["properties"]:
            item_field_definition = schema["properties"][item_key]
            if (
                not item_field_definition
                or "auto_fill" not in item_field_definition
                or not item_field_definition["auto_fill"]
            ):
                continue
            model_attribute_key = to_snake(item_key)
            item_val = cls.get_attribute(model, model_attribute_key)
            if isinstance(item_val, IsaAbstractModel):
                is_empty = IsaAbstractModel.is_empty_model(item_val)
                if not is_empty:
                    return False
            elif item_val:
                return False
        return True


class AssayTechnique(IsaAbstractModel):
    name: Annotated[
        str, Field(description="Technique name used to identify metabolites.")
    ] = ""
    main_technique: Annotated[
        Literal["MS", "NMR"],
        Field(description="Main category of metabolite identification technique."),
    ] = ""
    technique: Annotated[str, Field(description="Technique")] = ""
    sub_technique: Annotated[str, Field(description="Sub-technique")] = ""

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return self.__str__()


class OntologyItem(IsaAbstractModel):
    term: Annotated[str, Field(description="Ontology term.")] = ""
    term_source_ref: Annotated[
        str,
        Field(
            description="Source reference name of ontology term. e.g., EFO, OBO, NCIT."
        ),
    ] = ""
    term_accession_number: Annotated[
        str, Field(description="Accession number of ontology term.")
    ] = ""

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
    organism: Annotated[OntologyItem, Field(description="Organism ontology value.")] = (
        OntologyItem()
    )
    organism_part: Annotated[
        OntologyItem, Field(description="Organism part ontology value.")
    ] = OntologyItem()
    variant: Annotated[OntologyItem, Field(description="Variant ontology value.")] = (
        OntologyItem()
    )
    sample_type: Annotated[
        OntologyItem, Field(description="Sample type ontology value.")
    ] = OntologyItem()

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
    value: Annotated[str, Field(description="")] = ""
    unit: Annotated[OntologyItem, Field(description="")] = OntologyItem()


class ProtocolField(MetabolightsBaseModel):
    header_name: Annotated[str, Field(description="")] = ""


class ProtocolOntologyItem(ProtocolField):
    data: Annotated[List[OntologyItem], Field(description="")] = []


class ProtocolTextItem(ProtocolField):
    data: Annotated[List[str], Field(description="")] = []


class ProtocolNumericOntologyItem(ProtocolField):
    data: Annotated[List[NumericItem], Field(description="")] = []


class ProtocolItem(MetabolightsBaseModel):
    name: Annotated[str, Field(description="")] = ""
    text_fields: Annotated[Dict[str, ProtocolTextItem], Field(description="")] = {}
    numeric_fields: Annotated[
        Dict[str, ProtocolNumericOntologyItem], Field(description="")
    ] = {}
    ontology_fields: Annotated[
        Dict[str, ProtocolOntologyItem], Field(description="")
    ] = {}


class ProtocolFields(MetabolightsBaseModel):
    name: Annotated[str, Field(description="")] = ""
    text_fields: Annotated[Dict[str, ProtocolTextItem], Field(description="")] = {}
    numeric_fields: Annotated[
        Dict[str, ProtocolNumericOntologyItem], Field(description="")
    ] = {}
    ontology_fields: Annotated[
        Dict[str, ProtocolOntologyItem], Field(description="")
    ] = {}

    additional_text_fields: Annotated[
        List[ProtocolTextItem], Field(description="Additional text")
    ] = []
    additional_numeric_fields: Annotated[
        List[ProtocolNumericOntologyItem], Field(description="")
    ] = []
    additional_ontology_fields: Annotated[
        List[ProtocolOntologyItem], Field(description="")
    ] = []


class Comment(IsaAbstractModel):
    name: Annotated[str, Field(description="Name of comment")] = ""
    value: Annotated[Union[str, List[str]], Field(description="Values of comment")] = []

    @field_validator("value", mode="before")
    @classmethod
    def validate_value(cls, value) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        else:
            return [str(value)]


class IsaTableColumn(IsaAbstractModel):
    column_index: Annotated[
        Union[int, None],
        Field(description="Index of column in ISA Table. First column index is 0."),
    ] = None

    column_name: Annotated[
        str,
        Field(
            description="Unique name of column. "
            "It is same if column header is unique in ISA table."
        ),
    ] = ""

    column_header: Annotated[str, Field(description="Header of ISA table column.")] = ""

    additional_columns: Annotated[
        List[str],
        Field(
            description="Linked column names. If column is ontology or "
            "a column with unit ontology column, it lists the following column headers."
        ),
    ] = []

    column_category: Annotated[
        str,
        Field(
            description="Column category. e.g., Parameter Value, Factor Value, protocol"
        ),
    ] = ""

    column_structure: Annotated[
        ColumnsStructure, Field(description="Structure of column in ISA table.")
    ] = ColumnsStructure.SINGLE_COLUMN

    column_prefix: Annotated[
        str, Field(description="Column prefix if header has a value between [].")
    ] = ""

    default_value: Annotated[
        str,
        Field(description="Default value", exclude=True),
    ] = ""

    column_search_pattern: Annotated[
        str,
        Field(
            description="Search regex expression to fetch value "
            "if header has a value between []."
        ),
    ] = ""

    def __hash__(self):
        return hash(self.column_name)


class IsaTable(IsaAbstractModel):
    columns: Annotated[
        List[str],
        Field(
            description="Unique column names of ISA table. "
            "If there are duplicate column headers, column names are created "
            "with the following pattern: header name + '.X' "
            "where X is sequential number for each duplicate header name."
        ),
    ] = []

    headers: Annotated[
        List[IsaTableColumn],
        Field(
            description="Metadata of ISA table columns. "
            "e.i., header name, column name, column index"
        ),
    ] = []

    data: Annotated[
        Dict[str, List[str]], Field(description="Data columns and their row values.")
    ] = {}

    row_indices: Annotated[
        List[int],
        Field(
            description="Current rows' positions in ISA table. e.g., [2, 3, 5]: "
            "First three rows of 'data' are 2nd, 3th and 5th rows in ISA Table."
        ),
    ] = []

    column_indices: Annotated[
        List[int], Field(description="Current columns' positions in ISA table.")
    ] = []

    filtered_total_row_count: Annotated[
        int, Field(description="Total row count after filter operations.")
    ] = 0

    row_offset: Annotated[
        int, Field(description="Skipped rows after filter operations.")
    ] = 0

    row_count: Annotated[
        int,
        Field(description="Row count listed in this table after filter operations."),
    ] = 0

    total_row_count: Annotated[
        int, Field(description="Total row count in ISA table file.")
    ] = 0

    selected_column_count: Annotated[
        int, Field(description="Number of selected columns in this table file.")
    ] = 0

    total_column_count: Annotated[
        int, Field(description="Number of all columns in ISA table file.")
    ] = 0

    filter_options: Annotated[
        List[TsvFileFilterOption],
        Field(description="Applied filters on ISA table file."),
    ] = []

    sort_options: Annotated[
        List[TsvFileSortOption],
        Field(description="Applied sort operations on ISA table file."),
    ] = []


class IsaTableFile(IsaAbstractModel):
    file_path: Annotated[
        str,
        Field(
            description="Relative file path of ISA table file "
            "(s_*.txt, a_*.txt, m_*.tsv)."
        ),
    ] = ""

    sha256_hash: Annotated[
        str,
        Field(description="SHA256 hash value of ISA table file."),
    ] = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    table: Annotated[
        IsaTable,
        Field(description="All or partial content of ISA table file."),
    ] = IsaTable()
