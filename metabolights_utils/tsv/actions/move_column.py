import pathlib
import uuid

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseTsvAction


class MoveColumnTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvMoveColumnAction,
        read_encoding: str = "utf-8",
        write_encoding: str = "utf-8",
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.action_type != actions.TsvActionType.MOVE_COLUMN:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvMoveColumnAction = action
        source_column_index = action.source_column_index
        source_column_header = action.source_column_header
        new_column_index = action.new_column_index

        if not action.id:
            uuid_value = str(uuid.uuid4().hex)
            action.id = uuid_value

        try:
            with source_file_path.open("r", encoding=read_encoding) as source:
                header_line = source.readline()
                header_names = header_line.strip("\n").split("\t")
                new_header_names = []
                if source_column_index < 0 or source_column_index >= len(header_names):
                    result.message = (
                        f"Source column index is not in range. {source_column_index}"
                    )
                    return result
                if new_column_index < 0 or new_column_index >= len(header_names):
                    result.message = (
                        f"New column index is not in range. {new_column_index}"
                    )
                    return result

                moved_header = header_names[source_column_index]
                if moved_header != source_column_header:
                    result.message = (
                        f"Input header name does not match the actual one for the index {source_column_index}."
                        + f"Expected: {source_column_header}, found: {moved_header}"
                    )
                    return result
                new_header_names = [x for x in header_names if x != source_column_index]
                new_header_names.insert(new_column_index, moved_header)

                with target_file_path.open("w", encoding=write_encoding) as target:
                    self.write_row(target, new_header_names)
                    for line in source:
                        row = line.strip("\n").split("\t")
                        moved_data = row[source_column_index]
                        new_row = [x for x in row if x != source_column_index]
                        new_row.insert(new_column_index, moved_data)
                        self.write_row(target, new_row)
            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
