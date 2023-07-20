from enum import Enum
from typing import Dict, List, Union

from pydantic import Field

from metabolights_utils.common import CamelCaseModel


class TsvColumnData(CamelCaseModel):
    header_name: str = Field(default="", description="Column header name")
    values: Dict[int, str] = Field(
        default={}, description="Row indices and cell values of the column"
    )


class TsvRowData(CamelCaseModel):
    values: Dict[int, str] = Field(
        default={}, description="Column indices and cell values of the column"
    )


class TsvCellData(CamelCaseModel):
    row_index: int = Field(default=-1, description="Row index of the cell")
    column_index: int = Field(default=-1, description="Column index of the cell")
    value: str = Field(default="", description="Value of the cell")


class TsvActionType(str, Enum):
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
    id: str = Field(default="", description="Id of the action. UUID is used as default")
    type: TsvActionType = Field(TsvActionType.NO_ACTION, description="Tsv action type")


class TsvAddRowsAction(TsvAction):
    type: str = Field(TsvActionType.ADD_ROW, description="Type of tsv action.")
    new_row_indices: List[int] = Field([], description="Position (index) of new rows.")
    row_data: Dict[int, TsvRowData] = Field(
        {},
        description="Row indices and row data."
        + "If there is no row data for the selected row index, an empty row will be added."
        + "If row data has missing column values, missing columns cells will be filled with empty string",
    )


class TsvAddColumnsAction(TsvAction):
    type: str = Field(TsvActionType.ADD_COLUMN, description="Type of tsv action.")
    columns: Dict[int, TsvColumnData] = Field(
        {}, description="Row indices and column data."
    )
    cell_default_values: Dict[int, str] = Field(
        {}, description="Column indices and default values of the selected column rows."
    )


class TsvDeleteRowsAction(TsvAction):
    type: str = TsvActionType.DELETE_ROW
    current_row_indices: List[int] = Field(
        [], description="Current row indices will be deleted."
    )


class TsvDeleteColumnsAction(TsvAction):
    type: str = TsvActionType.DELETE_COLUMN
    current_columns: Dict[int, str] = Field(
        {},
        description="Current column indices and headers will be deleted."
        + "If column index and header do not match, action will be cancelled.",
    )


class TsvMoveRowAction(TsvAction):
    type: str = TsvActionType.MOVE_ROW
    source_row_index: int = Field(
        -1, description="Source row index that will be moved."
    )
    new_row_index: int = Field(-1, description="New row index of the selected row.")


class TsvMoveColumnAction(TsvAction):
    type: str = TsvActionType.MOVE_COLUMN
    source_column_index: int = Field(
        -1, description="Source column index that will be moved."
    )
    source_column_header: str = Field(
        "",
        description="Source column header that will be moved to verify the selected column.",
    )
    new_column_index: int = Field(
        -1, description="New column index of the selected column."
    )


class TsvCopyRowAction(TsvAction):
    type: str = TsvActionType.COPY_ROW
    source_row_index: int = Field(
        -1, description="Source row index that will be copied."
    )
    target_row_indices: List[int] = []
    selected_column_indices: List[int] = Field(
        [],
        description="Column indices will be copied. Set empty list to copy all columns of the selected row",
    )


class TsvCopyColumnAction(TsvAction):
    type: str = TsvActionType.COPY_COLUMN
    source_column_index: int = Field(-1, description="Source colum index")
    source_column_header: Union[None, str] = Field(
        "", description="Source colum header to verify."
    )
    target_columns: Dict[int, str] = Field(
        {}, description="target colum indices and headers."
    )
    selected_row_indices: List[int] = Field(
        [],
        description="Row indices. Set empty list to copy all rows of the selected column",
    )


class TsvUpdateRowsAction(TsvAction):
    type: str = TsvActionType.UPDATE_ROW_DATA
    rows: Dict[int, TsvRowData] = Field(
        {},
        description="Row indices and updated row data",
    )


class TsvUpdateColumnsAction(TsvAction):
    type: str = TsvActionType.UPDATE_COLUMN_DATA
    columns: Dict[int, TsvColumnData] = Field(
        {},
        description="Column indices and updated column data",
    )


class TsvUpdateCellsAction(TsvAction):
    type: str = TsvActionType.UPDATE_CELL_DATA
    cells: List[TsvCellData] = Field(
        [],
        description="Updated cell data list",
    )


class TsvUpdateColumnHeaderAction(TsvAction):
    type: str = TsvActionType.UPDATE_COLUMN_HEADER
    new_headers: Dict[int, str] = Field(
        {},
        description="Column indices and updated column headers",
    )


class TsvActionResult(CamelCaseModel):
    action: TsvAction = Field(None, description="Applied action details.")
    success: bool = Field(False, description="Result of action.")
    message: str = Field("", description="Error or success message after action.")


class TsvActionReport(CamelCaseModel):
    results: List[TsvActionResult] = Field(
        [], description="Ordered results of the applied actions."
    )
    success: bool = Field(False, description="Result of all applied actions.")
    message: str = Field("", description="Message after  applied actions.")
    updated_file_sha256_hash: str = Field(
        "", description="Last SHA256 hash value of the updated file."
    )
