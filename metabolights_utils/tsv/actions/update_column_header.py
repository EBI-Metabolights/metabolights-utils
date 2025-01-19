import pathlib
import uuid
from typing import Dict

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseTsvAction


class UpdateColumnHeadersTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvUpdateColumnHeaderAction,
        read_encoding: str = "utf-8",
        write_encoding: str = "utf-8",
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.action_type != actions.TsvActionType.UPDATE_COLUMN_HEADER:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvUpdateColumnHeaderAction = action

        headers: Dict[int, str] = action.new_headers if action.new_headers else {}

        column_indices = list(headers.keys())
        column_indices.sort()

        if not action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value

        try:
            with source_file_path.open("r", encoding=read_encoding) as source:
                header_line = source.readline()
                header_names = header_line.strip("\n").split("\t")
                column_count = len(header_names)
                for column_idx in column_indices:
                    if column_idx < column_count and headers[column_idx]:
                        header_names[column_idx] = headers[column_idx]
                    else:
                        name = headers[column_idx] if headers[column_idx] else ""
                        result.message = f"Invalid column index {column_idx} with column name '{name}'"
                        return result
                with target_file_path.open("w", encoding=write_encoding) as target:
                    self.write_row(target, header_names)
                    for line in source:
                        target.write(line)
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
