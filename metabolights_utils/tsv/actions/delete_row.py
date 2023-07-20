import pathlib
import uuid
from typing import List

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseTsvAction


class DeleteRowsTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvDeleteRowsAction,
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.type != actions.TsvActionType.DELETE_ROW:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvDeleteRowsAction = action
        target_row_indices: List[int] = action.current_row_indices

        if not target_row_indices:
            result.message = "There is not row index"
            return result

        row_indices = target_row_indices.copy()
        row_indices.sort()

        if action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value

        try:
            with open(source_file_path, "r") as source:
                header_line = source.readline()
                header_names = header_line.strip().split("\t")

                with open(target_file_path, "w") as target:
                    self.write_row(target, header_names)
                    row_index = -1
                    for line in source:
                        row_index += 1
                        if row_index in row_indices:
                            row_indices.remove(row_index)
                            continue
                        else:
                            target.write(line)

                    if len(row_indices):
                        result.message = f"Invalid row indices {', '.join(row_indices)}"
                        return result
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
