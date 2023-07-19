import datetime
import hashlib
import os
import pathlib
import shutil
import uuid
from typing import Dict, List, Union

from metabolights_utils.tsv.actions.add_column import AddColumnsActionHelper
from metabolights_utils.tsv.actions.add_row import AddRowsActionHelper
from metabolights_utils.tsv.actions.base import BaseActionHelper, TsvActionException
from metabolights_utils.tsv.actions.copy_column import CopyColumnActionHelper
from metabolights_utils.tsv.actions.copy_row import CopyRowActionHelper
from metabolights_utils.tsv.actions.delete_column import DeleteColumnsActionHelper
from metabolights_utils.tsv.actions.delete_row import DeleteRowsActionHelper
from metabolights_utils.tsv.actions.move_column import MoveColumnActionHelper
from metabolights_utils.tsv.actions.move_row import MoveRowActionHelper
from metabolights_utils.tsv.actions.update_cell import UpdateCellsActionHelper
from metabolights_utils.tsv.actions.update_column import UpdateColumnsActionHelper
from metabolights_utils.tsv.actions.update_column_header import (
    UpdateColumnHeadersActionHelper,
)
from metabolights_utils.tsv.actions.update_row import UpdateRowsActionHelper
from metabolights_utils.tsv.model import (
    TsvAction,
    TsvActionName,
    TsvActionReport,
    TsvActionResult,
)

ISA_TABLE_ACTION_HELPERS: Dict[TsvActionName, BaseActionHelper] = {}
ISA_TABLE_ACTION_HELPERS[TsvActionName.ADD_ROW] = AddRowsActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.DELETE_ROW] = DeleteRowsActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.UPDATE_ROW_DATA] = UpdateRowsActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.COPY_ROW] = CopyRowActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.MOVE_ROW] = MoveRowActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.ADD_COLUMN] = AddColumnsActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.DELETE_COLUMN] = DeleteColumnsActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.COPY_COLUMN] = CopyColumnActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.UPDATE_COLUMN_DATA] = UpdateColumnsActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.MOVE_COLUMN] = MoveColumnActionHelper()
ISA_TABLE_ACTION_HELPERS[
    TsvActionName.UPDATE_COLUMN_HEADER
] = UpdateColumnHeadersActionHelper()
ISA_TABLE_ACTION_HELPERS[TsvActionName.UPDATE_CELL_DATA] = UpdateCellsActionHelper()


class TsvFileUpdater:
    def apply_actions(
        self,
        file_path: Union[str, pathlib.Path],
        file_sha256_hash: str,
        actions: List[TsvAction],
    ) -> TsvActionReport:
        report = TsvActionReport()
        if not file_path:
            report.message = "Invalid input for file path"
            return report
        if not file_sha256_hash:
            report.message = "Invalid input for file hash value"
            return report
        if not file_sha256_hash:
            report.message = "Invalid input for file hash value"
            return report

        if not actions:
            report.message = "Invalid input for action list"
            return report

        if isinstance(file_path, pathlib.Path):
            file = file_path
        else:
            file = pathlib.Path(file_path)

        if not file.exists() or not file.is_file():
            report.message = (
                f"File '{str(file)}' does not exist or it is not a regular file."
            )
            return report
        sha256 = self.calculate_sha256(file)

        if sha256 != file_sha256_hash:
            report.message = f"SH256 of '{str(file)}' does not match the input value."
            return report

        task_id = str(uuid.uuid4().hex)
        timestamp = str(int(datetime.datetime.now().timestamp()))
        temp_folder = pathlib.Path(f"/tmp/isa_table_actions/{timestamp}/{task_id}")
        os.makedirs(str(temp_folder))

        file_copy_path = temp_folder / pathlib.Path(f"{file.name}_{task_id}")
        temp_source_file_path = temp_folder / pathlib.Path(
            f".{file.name}_{task_id}_temp_1"
        )
        temp_target_file_path = temp_folder / pathlib.Path(
            f".{file.name}_{task_id}_temp_2"
        )

        source_path = file_copy_path
        target_path = temp_target_file_path
        last_file = None
        try:
            for action in actions:
                if action.name not in ISA_TABLE_ACTION_HELPERS:
                    report.message = f"Upsupported action: action.name."
                    return report
            shutil.move(file, file_copy_path)
            for action in actions:
                helper = ISA_TABLE_ACTION_HELPERS[action.name]
                result: TsvActionResult = helper.apply_action(
                    source_path, target_path, action
                )
                last_file = target_path
                source_path = last_file
                target_path = (
                    temp_target_file_path
                    if source_path == temp_source_file_path
                    else temp_source_file_path
                )

                report.results.append(result)
                if not result.success:
                    raise TsvActionException(message=result.message)
            new_sha256 = self.calculate_sha256(last_file)
            report.updated_file_sha256_hash = new_sha256
            report.success = True
        except Exception as exc:
            raise exc
        finally:
            if report.success and last_file:
                shutil.move(last_file, file)
            else:
                shutil.move(file_copy_path, file)
            shutil.rmtree(temp_folder)
        return report

    def calculate_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
