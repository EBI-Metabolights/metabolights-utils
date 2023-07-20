import pathlib
import uuid
from typing import Dict, List

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseTsvAction


class AddColumnsTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvAddColumnsAction,
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.type != actions.TsvActionType.ADD_COLUMN:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvAddColumnsAction = action

        column_data: Dict[int, actions.TsvColumnData] = (
            action.columns if action.columns else {}
        )
        if not column_data:
            result.message = "There is not column index"
            return result

        cell_default_values: Dict[int, str] = (
            action.cell_default_values if action.cell_default_values else {}
        )

        column_indices: List[int] = list(column_data.keys()).copy()
        column_indices.sort()

        if action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value

        try:
            with open(source_file_path, "r") as source:
                header_line = source.readline()
                header_names = header_line.strip().split("\t")
                for column_idx in column_indices:
                    if column_idx < 0:
                        column_idx = len(header_names)
                    default_value = (
                        cell_default_values[column_idx]
                        if column_idx in cell_default_values
                        and cell_default_values[column_idx]
                        else ""
                    )
                    value: actions.TsvColumnData = column_data[column_idx]
                    if not value or not value.header_name:
                        result.message = (
                            f"There is not header name for column index {column_idx}"
                        )
                        return result
                    header_names.insert(column_idx, value.header_name)

                with open(target_file_path, "w") as target:
                    self.write_row(target, header_names)
                    row_index = 0
                    for line in source:
                        row = line.strip().split("\t")
                        for column_idx in column_indices:
                            default_value = (
                                cell_default_values[column_idx]
                                if column_idx in cell_default_values
                                and cell_default_values[column_idx]
                                else ""
                            )
                            coloumn_data: actions.TsvColumnData = column_data[
                                column_idx
                            ]
                            value = (
                                coloumn_data.values[row_index]
                                if row_index in coloumn_data.values
                                else default_value
                            )
                            row.insert(column_idx, value)
                        self.write_row(target, row)
                        row_index += 1
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
