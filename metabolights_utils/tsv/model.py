from enum import Enum
from typing import Dict, List, Union

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.common import CamelCaseModel


class TsvColumnData(CamelCaseModel):
    header_name: Annotated[str, Field(description="Column header name")] = ""
    values: Annotated[
        Dict[int, str], Field(description="Row indices and cell values of the column")
    ] = {}


class TsvRowData(CamelCaseModel):
    values: Annotated[
        Dict[int, str],
        Field(description="Column indices and cell values of the column"),
    ] = {}


class TsvCellData(CamelCaseModel):
    row_index: Annotated[int, Field(description="Row index of the cell")] = -1
    column_index: Annotated[int, Field(description="Column index of the cell")] = -1
    value: Annotated[str, Field(description="Value of the cell")] = ""


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
    id: Annotated[
        str, Field(description="Id of the action. UUID is used as default")
    ] = ""
    action_type: Annotated[
        TsvActionType,
        Field(description="Tsv action type"),
    ] = TsvActionType.NO_ACTION


class TsvAddRowsAction(TsvAction):
    action_type: TsvActionType = TsvActionType.ADD_ROW
    new_row_indices: Annotated[
        List[int], Field(description="Position (index) of new rows.")
    ] = []
    row_data: Annotated[
        Dict[int, TsvRowData],
        Field(
            description="Row indices and row data."
            + "If there is no row data for the selected row index, an empty row will be added."
            + "If row data has missing column values, missing columns cells will be filled with empty string",
        ),
    ] = {}


class TsvAddColumnsAction(TsvAction):
    action_type: TsvActionType = TsvActionType.ADD_COLUMN
    columns: Annotated[
        Dict[int, TsvColumnData], Field(description="Row indices and column data.")
    ] = {}
    cell_default_values: Annotated[
        Dict[int, str],
        Field(
            description="Column indices and default values of the selected column rows."
        ),
    ] = {}


class TsvDeleteRowsAction(TsvAction):
    action_type: TsvActionType = TsvActionType.DELETE_ROW
    current_row_indices: Annotated[
        List[int], Field(description="Current row indices will be deleted.")
    ] = []


class TsvDeleteColumnsAction(TsvAction):
    action_type: TsvActionType = TsvActionType.DELETE_COLUMN
    current_columns: Annotated[
        Dict[int, str],
        Field(
            description="Current column indices and headers will be deleted. "
            "If column index and header do not match, action will be cancelled.",
        ),
    ] = {}


class TsvMoveRowAction(TsvAction):
    action_type: TsvActionType = TsvActionType.MOVE_ROW
    source_row_index: Annotated[
        int, Field(description="Source row index that will be moved.")
    ] = -1
    new_row_index: Annotated[
        int, Field(description="New row index of the selected row.")
    ] = -1


class TsvMoveColumnAction(TsvAction):
    action_type: TsvActionType = TsvActionType.MOVE_COLUMN
    source_column_index: Annotated[
        int, Field(description="Source column index that will be moved.")
    ] = -1
    source_column_header: Annotated[
        str,
        Field(
            description="Source column header that will be moved to verify the selected column.",
        ),
    ] = ""
    new_column_index: Annotated[
        int, Field(description="New column index of the selected column.")
    ] = -1


class TsvCopyRowAction(TsvAction):
    action_type: str = TsvActionType.COPY_ROW
    source_row_index: Annotated[
        int, Field(description="Source row index that will be copied.")
    ] = -1
    target_row_indices: Annotated[
        List[int], Field(description="Target row indices.")
    ] = []
    selected_column_indices: Annotated[
        List[int],
        Field(
            description="Column indices will be copied. Set empty list to copy all columns of the selected row",
        ),
    ] = []


class TsvCopyColumnAction(TsvAction):
    action_type: TsvActionType = TsvActionType.COPY_COLUMN
    source_column_index: Annotated[int, Field(description="Source colum index")] = -1
    source_column_header: Annotated[
        Union[None, str], Field(description="Source colum header to verify.")
    ] = ""
    target_columns: Annotated[
        Dict[int, str], Field(description="target colum indices and headers.")
    ] = {}
    selected_row_indices: Annotated[
        List[int],
        Field(
            description="Row indices. Set empty list to copy all rows of the selected column",
        ),
    ] = []


class TsvUpdateRowsAction(TsvAction):
    action_type: str = TsvActionType.UPDATE_ROW_DATA
    rows: Annotated[
        Dict[int, TsvRowData],
        Field(
            description="Row indices and updated row data",
        ),
    ] = {}


class TsvUpdateColumnsAction(TsvAction):
    action_type: TsvActionType = TsvActionType.UPDATE_COLUMN_DATA
    columns: Annotated[
        Dict[int, TsvColumnData],
        Field(
            description="Column indices and updated column data",
        ),
    ] = {}


class TsvUpdateCellsAction(TsvAction):
    action_type: TsvActionType = TsvActionType.UPDATE_CELL_DATA
    cells: Annotated[
        List[TsvCellData], Field(description="Updated cell data list")
    ] = []


class TsvUpdateColumnHeaderAction(TsvAction):
    action_type: TsvActionType = TsvActionType.UPDATE_COLUMN_HEADER
    new_headers: Annotated[
        Dict[int, str], Field(description="Column indices and new column headers")
    ] = {}
    current_headers: Annotated[
        Dict[int, str], Field(description="Current column indices and column headers")
    ] = {}


class TsvActionResult(CamelCaseModel):
    action: Annotated[TsvAction, Field(description="Applied action details.")] = (
        TsvAction()
    )
    success: Annotated[bool, Field(description="Result of action.")] = False
    message: Annotated[
        str, Field(description="Error or success message after action.")
    ] = ""


class TsvActionReport(CamelCaseModel):
    results: Annotated[
        List[TsvActionResult],
        Field(description="Ordered results of the applied actions."),
    ] = []
    success: Annotated[bool, Field(description="Result of all applied actions.")] = (
        False
    )
    message: Annotated[str, Field(description="Message after  applied actions.")] = ""
    updated_file_sha256_hash: Annotated[
        str, Field(description="Last SHA256 hash value of the updated file.")
    ] = ""
