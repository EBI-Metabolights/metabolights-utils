import pathlib
import uuid
from typing import Dict, List

from metabolights_utils.tsv import model as actions
from metabolights_utils.tsv.actions.base import BaseTsvAction


class CopyColumnTsvAction(BaseTsvAction):
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvCopyColumnAction,
        read_encoding: str = "utf-8",
        write_encoding: str = "utf-8",
    ) -> actions.TsvActionResult:
        result: actions.TsvActionResult = actions.TsvActionResult(action=action)
        if action.action_type != actions.TsvActionType.COPY_COLUMN:
            result.message = "Action name is not valid"
            return result

        action: actions.TsvCopyColumnAction = action
        source_column_index = action.source_column_index
        source_column_header = action.source_column_header

        columns: Dict[int, str] = action.target_columns if action.target_columns else {}
        selected_row_indices = (
            set(action.selected_row_indices) if action.selected_row_indices else None
        )
        if not columns:
            result.message = "There is not target column index"
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
                source_column_found: bool = False
                for column_idx, value in enumerate(header_names):
                    if column_idx == source_column_index:
                        if source_column_header != value:
                            result.message = f"Input header name does not match the actual one for index {column_idx}. Expected: {source_column_header}, found: {value}"
                            return result
                        source_column_found = True
                        break

                if not source_column_found:
                    result.message = (
                        f"Source column index is not found: {source_column_index}."
                    )
                    return result
                invalid_targets = []
                for column_idx in columns:
                    if column_idx >= len(header_names) and column_idx < 0:
                        invalid_targets.append(column_idx)

                if invalid_targets:
                    result.message = f"Target column indices are not valid: {', '.join(invalid_targets)}."
                    return result

                with target_file_path.open("w", encoding=write_encoding) as target:
                    self.write_row(target, header_names)
                    row_index = 0
                    for line in source:
                        row = line.strip("\n").split("\t")
                        for column_idx in columns:
                            if (
                                not selected_row_indices
                                or row_index in selected_row_indices
                            ):
                                row[column_idx] = row[source_column_index]

                        self.write_row(target, row)
                        row_index += 1

            result.success = True
        except Exception as exc:
            result.message = f"{str(exc)}"

        return result
