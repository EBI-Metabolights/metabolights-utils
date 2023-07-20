import pathlib
import sys
import uuid
from typing import Dict, List

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseTsvAction


class MoveRowTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvMoveRowAction,
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.type != actions.TsvActionType.MOVE_ROW:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvMoveRowAction = action
        new_row_index = action.new_row_index

        if new_row_index is None or new_row_index < 0:
            result.message = "There is no new row index"
            return result

        source_index = action.source_row_index

        if source_index is None or source_index < 0:
            result.message = "There is not source row index"
            return result

        if action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value
        new_source_index = source_index
        moved_row = None
        if source_index >= new_row_index:
            with open(source_file_path, "r") as source:
                source.readline()
                row_index = -1
                for line in source:
                    row_index += 1
                    if row_index > source_index:
                        break
                    if row_index == source_index:
                        moved_row = line.strip().split("\t")
                        break

            if not moved_row:
                result.message = "The row will be moved is not found"
                return result
            new_source_index += 1

        moved = False
        source_deleted = False
        try:
            with open(source_file_path, "r") as source:
                header_line = source.readline()

                with open(target_file_path, "w") as target:
                    target.write(header_line)
                    row_index = -1
                    for line in source:
                        row_index += 1
                        if row_index == new_row_index and not moved:
                            self.write_row(target, moved_row)
                            moved = True
                            if source_deleted or row_index != source_index:
                                target.write(line)
                                row_index += 1
                        else:
                            if row_index == new_source_index and not source_deleted:
                                source_deleted = True
                                moved_row = line.strip().split("\t")
                                row_index -= 1
                            else:
                                target.write(line)
                    if new_row_index == row_index + 1 and not moved:
                        self.write_row(target, moved_row)
                        moved = True

            if not moved:
                result.message = f"Move is failed"
                return result
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
