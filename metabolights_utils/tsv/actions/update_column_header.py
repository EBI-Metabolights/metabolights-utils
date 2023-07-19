import pathlib
import sys
import uuid
from typing import Dict, List

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseActionHelper


class UpdateColumnHeadersActionHelper(BaseActionHelper):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvUpdateColumnHeaderAction,
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.name != actions.TsvActionName.UPDATE_COLUMN_HEADER:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvUpdateColumnHeaderAction = action

        headers: Dict[int, str] = action.new_headers if action.new_headers else {}

        column_indices = list(headers.keys())
        column_indices.sort()

        if action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value

        try:
            with open(source_file_path, "r") as source:
                header_line = source.readline()
                header_names = header_line.strip().split("\t")
                column_count = len(header_names)
                for column_idx in column_indices:
                    if column_idx < column_count and headers[column_idx]:
                        header_names[column_idx] = headers[column_idx]
                    else:
                        headers[column_idx] = (
                            headers[column_idx] if headers[column_idx] else ""
                        )
                        result.message = f"Invalid column index {column_idx} with column name '{headers[column_idx]}'"
                        return result
                with open(target_file_path, "w") as target:
                    self.write_row(target, header_names)
                    for line in source:
                        target.write(line)
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
