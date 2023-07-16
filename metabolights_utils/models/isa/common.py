from enum import Enum
from typing import Dict, List, Union

from pydantic import BaseModel, Extra, Field

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.isa.enums import ColumnsStructure

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
            item_val = getattr(model, item_key)
            if isinstance(item_val, IsaAbstractModel):
                is_empty = IsaAbstractModel.is_empty_model(item_val)
                if not is_empty:
                    return False
            elif item_val:
                return False
        return True


class AssayTechnique(IsaAbstractModel):
    name: str = ""
    mainTechnique: str = ""
    technique: str = ""
    subTechnique: str = ""

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
    termSourceRef: str = ""
    termAccessionNumber: str = ""

    def __str__(self) -> str:
        if self.term:
            if self.termSourceRef or self.termAccessionNumber:
                return f"{self.term} [{self.termSourceRef}:{self.termAccessionNumber}]"
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
    organismPart: OntologyItem = OntologyItem()
    variant: OntologyItem = OntologyItem()
    sampleType: OntologyItem = OntologyItem()

    def __str__(self) -> str:
        if self.organism and self.organismPart and self.variant and self.sampleType:
            return ":".join(
                [
                    self.organism.__str__(),
                    self.organismPart.__str__(),
                    self.variant.__str__(),
                    self.sampleType.__str__(),
                ]
            )

        if self.organism and self.organismPart and self.variant:
            return ":".join(
                [
                    self.organism.__str__(),
                    self.organismPart.__str__(),
                    self.variant.__str__(),
                ]
            )
        if self.organism and self.organismPart:
            return ":".join([self.organism.__str__(), self.organismPart.__str__()])
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
    headerName: str = ""


class ProtocolOntologyItem(ProtocolField):
    data: List[OntologyItem] = []


class ProtocolTextItem(ProtocolField):
    data: List[str] = []


class ProtocolNumericOntologyItem(ProtocolField):
    data: List[NumericItem] = []


class ProtocolItem(BaseModel):
    name: str = ""
    textFields: Dict[str, ProtocolTextItem] = {}
    numericFields: Dict[str, ProtocolNumericOntologyItem] = {}
    ontologyFields: Dict[str, ProtocolOntologyItem] = {}


class ProtocolFields(BaseModel):
    name: str = ""
    textFields: Dict[str, ProtocolTextItem] = {}
    numericFields: Dict[str, ProtocolNumericOntologyItem] = {}
    ontologyFields: Dict[str, ProtocolOntologyItem] = {}

    additionalTextFields: List[ProtocolTextItem] = []
    additionalNumericFields: List[ProtocolNumericOntologyItem] = []
    additionalOntologyFields: List[ProtocolOntologyItem] = []


class Comment(IsaAbstractModel):
    name: str = ""
    value: List[str] = []


class IsaTableColumn(IsaAbstractModel):
    columnIndex: Union[int, str] = ""
    columnName: str = ""
    columnHeader: str = ""
    additionalColumns: List[str] = []
    columnCategory: str = ""
    colummnStructure: ColumnsStructure = ColumnsStructure.SINGLE_COLUMN
    columnPrefix: str = ""
    columnSearchPattern: str = ""

    def __hash__(self):
        return hash(self.columnName)


class FilterParameterType(str, Enum):
    AUTO = "AUTO"
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    DATETIME = "DATETIME"


class FilterOperation(str, Enum):
    CONTAINS = "like"
    EQUAL = "eq"
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"
    GREATER = "gt"
    GREATER_EQUAL = "ge"
    LESS = "lt"
    LESS_EQUAL = "le"
    REGEX = "regex"
    EMPTY = "empty"


class TsvFileFilterOption(BaseModel):
    column_name: str
    operation: FilterOperation = FilterOperation.CONTAINS
    parameter: Union[str, int, float] = ""
    parameter_type: FilterParameterType = FilterParameterType.AUTO
    case_sensitive: bool = True
    negate_result: bool = False
    default_datetime_pattern: str = "%m/%d/%Y"


class SortType(str, Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    DATETIME = "DATETIME"


class SortValueClassification(int, Enum):
    EMPTY = 1
    INVALID = 2
    VALID = 3


class TsvFileSortValueOrder(int, Enum):
    EMPTY_INVALID_VALID = 0o123
    EMPTY_VALID_INVALID = 0o132
    INVALID_EMPTY_VALID = 0o213
    INVALID_VALID_EMPTY = 0o231
    VALID_INVALID_EMPTY = 0o321
    VALID_EMPTY_INVALID = 0o312


class TsvFileSortOption(BaseModel):
    column_name: str
    reverse: bool = False
    column_sort_type: SortType = SortType.STRING
    case_sensitive: bool = True
    default_datetime_pattern: str = "%m/%d/%Y"
    value_order: TsvFileSortValueOrder = TsvFileSortValueOrder.VALID_EMPTY_INVALID


class IsaTable(IsaAbstractModel):
    columns: List[str] = Field([])
    headers: List[IsaTableColumn] = Field([])
    data: Dict[str, List[str]] = Field({})
    rowIndices: List[int] = []
    columnIndices: List[int] = []
    filteredTotalRowCount: int = 0
    rowOffset: int = 0
    rowCount: int = 0
    totalRowCount: int = 0
    selectedColumnCount: int = 0
    totalColumnCount: int = 0
    filterOptions: List[TsvFileFilterOption] = []
    sortOptions: List[TsvFileSortOption] = []


class IsaTableFile(IsaAbstractModel):
    filePath: str = ""
    table: IsaTable = Field(IsaTable())
