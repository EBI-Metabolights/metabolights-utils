from typing import Dict, List, Union

from pydantic import BaseModel, Extra, Field

from metabolights_utils.models.isa.enums import ColumnsStructure


class IsaAbstractModel(BaseModel):
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


class ProtocolField(BaseModel):
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


class IsaTable(IsaAbstractModel):
    columns: List[str] = Field([])
    headers: List[IsaTableColumn] = Field([])
    data: Dict[str, List[str]] = Field({})
    rowOffset: int = 0
    rowCount: int = 0
    totalRowCount: int = 0


class IsaTableFile(IsaAbstractModel):
    filePath: str = ""
    table: IsaTable = Field(IsaTable())
