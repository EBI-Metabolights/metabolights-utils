import datetime
import pathlib
import shutil
import uuid
from typing import Dict, List, Union

from metabolights_utils.tsv.actions.add_column import AddColumnsTsvAction
from metabolights_utils.tsv.actions.add_row import AddRowsTsvAction
from metabolights_utils.tsv.actions.base import BaseTsvAction, TsvActionException
from metabolights_utils.tsv.actions.copy_column import CopyColumnTsvAction
from metabolights_utils.tsv.actions.copy_row import CopyRowTsvAction
from metabolights_utils.tsv.actions.delete_column import DeleteColumnsTsvAction
from metabolights_utils.tsv.actions.delete_row import DeleteRowsTsvAction
from metabolights_utils.tsv.actions.move_column import MoveColumnTsvAction
from metabolights_utils.tsv.actions.move_row import MoveRowTsvAction
from metabolights_utils.tsv.actions.update_cell import UpdateCellsTsvAction
from metabolights_utils.tsv.actions.update_column import UpdateColumnsTsvAction
from metabolights_utils.tsv.actions.update_column_header import (
    UpdateColumnHeadersTsvAction,
)
from metabolights_utils.tsv.actions.update_row import UpdateRowsTsvAction
from metabolights_utils.tsv.model import (
    TsvAction,
    TsvActionReport,
    TsvActionResult,
    TsvActionType,
)
from metabolights_utils.utils.hash_utils import MetabolightsHashUtils as HashUtils

TSV_FILE_ACTIONS: Dict[TsvActionType, BaseTsvAction] = {}
TSV_FILE_ACTIONS[TsvActionType.ADD_ROW] = AddRowsTsvAction()
TSV_FILE_ACTIONS[TsvActionType.DELETE_ROW] = DeleteRowsTsvAction()
TSV_FILE_ACTIONS[TsvActionType.UPDATE_ROW_DATA] = UpdateRowsTsvAction()
TSV_FILE_ACTIONS[TsvActionType.COPY_ROW] = CopyRowTsvAction()
TSV_FILE_ACTIONS[TsvActionType.MOVE_ROW] = MoveRowTsvAction()
TSV_FILE_ACTIONS[TsvActionType.ADD_COLUMN] = AddColumnsTsvAction()
TSV_FILE_ACTIONS[TsvActionType.DELETE_COLUMN] = DeleteColumnsTsvAction()
TSV_FILE_ACTIONS[TsvActionType.COPY_COLUMN] = CopyColumnTsvAction()
TSV_FILE_ACTIONS[TsvActionType.UPDATE_COLUMN_DATA] = UpdateColumnsTsvAction()
TSV_FILE_ACTIONS[TsvActionType.MOVE_COLUMN] = MoveColumnTsvAction()
TSV_FILE_ACTIONS[TsvActionType.UPDATE_COLUMN_HEADER] = UpdateColumnHeadersTsvAction()
TSV_FILE_ACTIONS[TsvActionType.UPDATE_CELL_DATA] = UpdateCellsTsvAction()


class TsvFileUpdater:
    def apply_actions(
        self,
        file_path: Union[str, pathlib.Path],
        file_sha256_hash: str,
        actions: List[TsvAction],
        read_encoding: str = "utf-8",
        write_encoding: str = "utf-8",
        temp_path: str = "/tmp/mtb-utils-temp",
    ) -> TsvActionReport:
        report: TsvActionReport = TsvActionReport()
        if not file_path:
            report.message = "Invalid input for file path"
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
        sha256 = HashUtils.sha256sum(file, convert_to_linux_line_ending=True)

        if sha256 != file_sha256_hash:
            report.message = f"SH256 of '{str(file)}' does not match the input value."
            return report

        task_id = str(uuid.uuid4().hex)
        temp_root_path = (
            pathlib.Path(temp_path.rstrip("/"))
            if temp_path
            else pathlib.Path("/tmp/mtb-utils-temp")
        )
        timestamp = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
        temp_folder = temp_root_path / pathlib.Path(
            f"isa_table_actions/{timestamp}/{task_id}"
        )
        temp_folder.mkdir(parents=True, exist_ok=True)
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
                if action.action_type not in TSV_FILE_ACTIONS:
                    report.message = "Unsupported action: action.action_type."
                    return report
            shutil.move(file, file_copy_path)
            for action in actions:
                helper = TSV_FILE_ACTIONS[action.action_type]
                result: TsvActionResult = helper.apply_action(
                    source_path,
                    target_path,
                    action,
                    read_encoding=read_encoding,
                    write_encoding=write_encoding,
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
            new_sha256 = HashUtils.sha256sum(last_file)
            report.updated_file_sha256_hash = new_sha256
            report.success = True
        except TsvActionException as exc:
            report.message = exc.message
        except Exception as exc:
            report.message = str(exc)
        finally:
            if report.success and last_file:
                shutil.move(last_file, file)
            else:
                shutil.move(file_copy_path, file)
            shutil.rmtree(temp_folder)
        return report
