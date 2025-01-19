import pathlib
import uuid
from typing import Dict

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseTsvAction


class UpdateRowsTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvUpdateRowsAction,
        read_encoding: str = "utf-8",
        write_encoding: str = "utf-8",
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.action_type != actions.TsvActionType.UPDATE_ROW_DATA:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvUpdateRowsAction = action

        row_data: Dict[int, actions.TsvRowData] = action.rows if action.rows else {}
        if not row_data:
            result.message = "There is not row data"
            return result

        row_indices = list(row_data.keys())
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
                            input_row = row_data[row_index]
                            new_row = self.get_updated_row(empty_row, input_row)
                            self.write_row(target, new_row)
                            row_indices.remove(row_index)
                        else:
                            target.write(line)

                    if len(row_indices):
                        result.message = f"Invalid row indices {', '.join([str(x) for x in row_indices])}"
                        return result
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
