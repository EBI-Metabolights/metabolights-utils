import pathlib
import uuid
from typing import List, Set

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseTsvAction


class CopyRowTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvCopyRowAction,
        read_encoding: str = "utf-8",
        write_encoding: str = "utf-8",
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.action_type != actions.TsvActionType.COPY_ROW:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvCopyRowAction = action
        target_row_indices: List[int] = action.target_row_indices
        selected_column_indices: Set[int] = set(action.selected_column_indices)
        if not target_row_indices:
            result.message = "There is no target row index"
            return result

        source_index = action.source_row_index

        if not source_index or source_index < 0:
            result.message = "There is not row index"
            return result

        row_indices = target_row_indices.copy()
        row_indices.sort()

        if not action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value
        copied_row = None
        with source_file_path.open("r", encoding=read_encoding) as source:
            source.readline()
            row_index = 0
            for line in source:
                if row_index > source_index:
                    break
                if row_index == source_index:
                    copied_row = line.strip("\n").split("\t")
                    break
                row_index += 1
        if not copied_row:
            result.message = "Row will be copied is not found"
            return result

        try:
            with source_file_path.open("r", encoding=read_encoding) as source:
                header_line = source.readline()

                with target_file_path.open("w", encoding=write_encoding) as target:
                    target.write(header_line)
                    row_index = 0
                    for line in source:
                        if row_index in row_indices:
                            if not selected_column_indices:
                                self.write_row(target, copied_row)
                            else:
                                new_row = line.strip("\n").split("\t")
                                for index in selected_column_indices:
                                    new_row[index] = copied_row[index]
                                    self.write_row(target, new_row)
                            row_indices.remove(row_index)
                        else:
                            target.write(line)
                        row_index += 1

                    if len(row_indices):
                        result.message = (
                            f"Invalid target row indices {', '.join(row_indices)}"
                        )
                        return result
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
