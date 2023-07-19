import pathlib
import sys
import uuid
from typing import Dict, List

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseActionHelper


class UpdateCellsActionHelper(BaseActionHelper):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvUpdateCellsAction,
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.name != actions.TsvActionName.UPDATE_CELL_DATA:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvUpdateCellsAction = action

        cells: List[actions.TsvCellData] = action.cells if action.cells else []

        if not cells:
            result.message = "There is no cell"
            return result

        cells.sort(key=lambda x: (x.row_index, x.column_index))
        row_data: Dict[idx, actions.TsvRowData] = {}
        for idx, val in enumerate(cells):
            row_idx = val.row_index
            col_idx = val.column_index
            if row_idx not in row_data:
                row_data[row_idx] = actions.TsvRowData()
            data: actions.TsvRowData = row_data[row_idx]
            data.values[col_idx] = val.value

        row_indices = {x.row_index for x in cells}
        column_indices = {x.column_index for x in cells}

        if action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value

        try:
            with open(source_file_path, "r") as source:
                header_line = source.readline()
                header_names = header_line.strip().split("\t")
                invalid_column_indices = [
                    x for x in column_indices if x < 0 or x > len(header_names)
                ]
                if invalid_column_indices:
                    result.message = (
                        f"Invalid column indices: {', '.join(invalid_column_indices)}"
                    )
                    return result

                with open(target_file_path, "w") as target:
                    self.write_row(target, header_names)
                    row_index = 0
                    for line in source:
                        row = line.strip().split("\t")
                        if row_index in row_data:
                            row_data_item = row_data[row_index]
                            for column_idx in row_data_item.values:
                                row[column_idx] = row_data_item.values[column_idx]
                            if row_index in row_indices:
                                row_indices.remove(row_index)

                        self.write_row(target, row)
                        row_index += 1
                    if row_indices:
                        result.message = (
                            f"Invalid row indices: {', '.join(row_indices)}"
                        )
                        return result
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
