import pathlib
import uuid
from typing import Dict, List

from metabolights_utils.tsv.actions.base import BaseTsvAction
from metabolights_utils.tsv.model import (
    TsvActionResult,
    TsvActionType,
    TsvAddRowsAction,
    TsvRowData,
)


class AddRowsTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: TsvAddRowsAction,
        read_encoding: str = "utf-8",
        write_encoding: str = "utf-8",
    ) -> TsvActionResult:
        result: TsvActionResult = TsvActionResult(action=action)
        if action.action_type != TsvActionType.ADD_ROW:
            result.message = "Action name is not valid"
            return result

        action: TsvAddRowsAction = action
        target_row_indices: List[int] = action.new_row_indices

        if not target_row_indices:
            result.message = "There is not row index"
            return result

        row_data: Dict[int, TsvRowData] = action.row_data if action.row_data else {}

        row_indices = target_row_indices.copy()
        row_indices.sort()

        if not action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value

        try:
            with source_file_path.open("r", encoding=read_encoding) as source:
                header_line = source.readline()
                header_names = header_line.strip("\n").split("\t")
                empty_row = [""] * len(header_names)

                with target_file_path.open("w", encoding=write_encoding) as target:
                    self.write_row(target, header_names)
                    row_index = -1
                    for line in source:
                        row_index += 1
                        if row_index in row_indices:
                            while row_index in row_indices:
                                input_row = (
                                    row_data[row_index]
                                    if row_index in row_data
                                    else None
                                )
                                if not input_row:
                                    self.write_row(target, empty_row)
                                else:
                                    new_row = self.get_updated_row(empty_row, input_row)
                                    self.write_row(target, new_row)
                                row_indices.remove(row_index)
                                row_index += 1
                        target.write(line)

                    if len(row_indices):
                        row_index += 1
                        while row_index in row_indices:
                            input_row = (
                                row_data[row_index] if row_index in row_data else None
                            )
                            if not input_row:
                                self.write_row(target, empty_row)
                            else:
                                new_row = self.get_updated_row(empty_row, input_row)
                                self.write_row(target, new_row)
                            row_indices.remove(row_index)
                            row_index += 1

                        if len(row_indices):
                            result.message = (
                                f"Invalid row indices {', '.join(row_indices)}"
                            )
                            return result
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
