from enum import Enum
from typing import Dict, List, Union

from pydantic import Field

from metabolights_utils.common import CamelCaseModel


class TsvColumnData(CamelCaseModel):
    header_name: str = ""
    values: Dict[int, str] = {}


class TsvRowData(CamelCaseModel):
    values: Dict[int, str] = {}


class TsvCellData(CamelCaseModel):
    row_index: int = -1
    column_index: int = -1
    value: str = ""


class TsvActionName(str, Enum):
    NO_ACTION = "no-action"
    ADD_ROW = "add-row"
    UPDATE_ROW_DATA = "update-row-data"
    DELETE_ROW = "delete-row"
    MOVE_ROW = "move-row"
    COPY_ROW = "copy-row"
    ADD_COLUMN = "add-column"
    UPDATE_COLUMN_DATA = "update-column-data"
    DELETE_COLUMN = "delete-column"
    MOVE_COLUMN = "move-column"
    COPY_COLUMN = "copy-column"
    UPDATE_COLUMN_HEADER = "update-column-name"
    UPDATE_CELL_DATA = "update-cell-data"


class TsvAction(CamelCaseModel):
    id: str = None
    name: TsvActionName = TsvActionName.NO_ACTION


class TsvAddRowsAction(TsvAction):
    name: str = TsvActionName.ADD_ROW
    new_row_indices: List[int] = []
    row_data: Dict[int, TsvRowData] = {}


class TsvAddColumnsAction(TsvAction):
    name: str = TsvActionName.ADD_COLUMN
    columns: Dict[int, TsvColumnData] = {}
    cell_default_values: Dict[int, str] = {}


class TsvDeleteRowsAction(TsvAction):
    name: str = TsvActionName.DELETE_ROW
    current_row_indices: List[int] = []


class TsvDeleteColumnsAction(TsvAction):
    name: str = TsvActionName.DELETE_COLUMN
    current_columns: Dict[int, str] = Field(
        {}, description="Current column indices and headers."
    )


class TsvMoveRowAction(TsvAction):
    name: str = TsvActionName.MOVE_ROW
    source_row_index: int = -1
    new_row_index: int = -1


class TsvMoveColumnAction(TsvAction):
    name: str = TsvActionName.MOVE_COLUMN
    source_column_index: Union[None, int] = None
    source_column_header: Union[None, str] = None
    new_column_index: Union[None, int] = None


class TsvCopyRowAction(TsvAction):
    name: str = TsvActionName.COPY_ROW
    source_row_index: int = -1
    target_row_indices: List[int] = []
    selected_column_indices: List[int] = Field(
        [], description="Column indices. If it is None or empty, Copy all columns"
    )


class TsvCopyColumnAction(TsvAction):
    name: str = TsvActionName.COPY_COLUMN
    source_column_index: int = Field(-1, description="Source colum index")
    source_column_header: Union[None, str] = Field(
        "", description="Source colum header to verify."
    )
    target_columns: Dict[int, str] = Field(
        {}, description="target colum indices and headers."
    )
    selected_row_indices: List[int] = Field(
        [], description="Row indices. If it is None or empty, Copy all rows"
    )


class TsvUpdateRowsAction(TsvAction):
    name: str = TsvActionName.UPDATE_ROW_DATA
    rows: Dict[int, TsvRowData] = {}


class TsvUpdateColumnsAction(TsvAction):
    name: str = TsvActionName.UPDATE_COLUMN_DATA
    columns: Dict[int, TsvColumnData] = {}


class TsvUpdateCellsAction(TsvAction):
    name: str = TsvActionName.UPDATE_CELL_DATA
    cells: List[TsvCellData] = []


class TsvUpdateColumnHeaderAction(TsvAction):
    name: str = TsvActionName.UPDATE_COLUMN_HEADER
    new_headers: Dict[int, str] = {}


class TsvActionResult(CamelCaseModel):
    action: TsvAction = None
    success: bool = False
    message: str = ""


class TsvActionReport(CamelCaseModel):
    results: List[TsvActionResult] = []
    success: bool = False
    message: str = ""
    updated_file_sha256_hash: str = ""
