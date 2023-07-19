import pathlib
import sys
import uuid
from typing import Dict, List

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseActionHelper


class UpdateColumnsActionHelper(BaseActionHelper):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvUpdateColumnsAction,
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.name != actions.TsvActionName.UPDATE_COLUMN_DATA:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvUpdateColumnsAction = action

        columns: Dict[int, actions.TsvColumnData] = (
            action.columns if action.columns else {}
        )

        if not columns:
            result.message = "There is not target column index"
            return result

        column_indices: List[int] = list(columns.keys()).copy()
        column_indices.sort()

        if action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value

        try:
            with open(source_file_path, "r") as source:
                header_line = source.readline()
                header_names = header_line.strip().split("\t")
                selected_columns: List[int] = []
                for column_idx, value in enumerate(header_names):
                    if column_idx in column_indices:
                        if columns[column_idx].header_name != value:
                            result.message = (
                                f"Input header name does not math the actual one for index {column_idx}."
                                + f"Expected: {columns[column_idx].header_name}, found: {value}"
                            )
                            return result
                        selected_columns.append(column_idx)

                if len(selected_columns) != len(column_indices):
                    invalid_indices = [
                        x for x in column_indices if x not in selected_columns
                    ]
                    result.message = (
                        f"Some column indices are not found :"
                        + f"{', '.join(invalid_indices)}"
                    )
                    return result

                invalid_targets = [
                    x for x in columns if x >= len(header_names) and x < 0
                ]
                if invalid_targets:
                    result.message = f"Target column indices are not valid: {', '.join(invalid_targets)}."
                    return result

                with open(target_file_path, "w") as target:
                    self.write_row(target, header_names)
                    row_index = 0
                    for line in source:
                        row = line.strip().split("\t")
                        for column_idx, value in columns.items():
                            column_data: actions.TsvColumnData = value
                            if (
                                not column_data.values
                                or row_index in column_data.values
                            ):
                                row[column_idx] = column_data.values[row_index]

                        self.write_row(target, row)
                        row_index += 1

            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
