import pathlib
import uuid
from typing import Dict, List

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseTsvAction


class DeleteColumnsTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvDeleteColumnsAction,
        read_encoding: str = "utf-8",
        write_encoding: str = "utf-8",
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.action_type != actions.TsvActionType.DELETE_COLUMN:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvDeleteColumnsAction = action

        columns: Dict[int, str] = (
            action.current_columns if action.current_columns else {}
        )
        if not columns:
            result.message = "There is not column index"
            return result

        column_indices: List[int] = list(columns.keys()).copy()
        column_indices.sort()

        if not action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value

        try:
            with source_file_path.open("r", encoding=read_encoding) as source:
                header_line = source.readline()
                header_names = header_line.strip("\n").split("\t")
                new_header_names = []
                for column_idx, value in enumerate(header_names):
                    if column_idx in column_indices:
                        header_name = columns[column_idx]
                        if header_name != value:
                            result.message = f"Input header name does not match the actual one for index {column_idx}. Expected: {header_name}, found: {value}"
                            return result
                        continue

                    new_header_names.append(value)

                with target_file_path.open("w", encoding=write_encoding) as target:
                    self.write_row(target, new_header_names)
                    for line in source:
                        row = line.strip("\n").split("\t")
                        new_row = [
                            x[1] for x in enumerate(row) if x[0] not in column_indices
                        ]
                        new_row.append(value)
                        self.write_row(target, new_row)
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
