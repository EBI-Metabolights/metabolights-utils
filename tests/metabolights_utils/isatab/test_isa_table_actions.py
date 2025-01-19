import os
import shutil
from pathlib import Path
from typing import Dict, List

from metabolights_utils.tsv.model import (
    TsvActionReport,
    TsvAddColumnsAction,
    TsvAddRowsAction,
    TsvCellData,
    TsvColumnData,
    TsvCopyColumnAction,
    TsvCopyRowAction,
    TsvDeleteColumnsAction,
    TsvDeleteRowsAction,
    TsvMoveColumnAction,
    TsvMoveRowAction,
    TsvRowData,
    TsvUpdateCellsAction,
    TsvUpdateColumnHeaderAction,
    TsvUpdateColumnsAction,
    TsvUpdateRowsAction,
)
from metabolights_utils.tsv.tsv_file_updater import TsvFileUpdater
from metabolights_utils.utils.filename_utils import join_path


def test_add_row_action_01():
    row = TsvRowData()
    row.values[1] = "Sample 1"
    row_data: Dict[int, TsvRowData] = {}
    row_data[8170] = row
    row = TsvRowData()
    row.values[2] = "Sample 5"
    row_data[8173] = row
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    action: TsvAddRowsAction = TsvAddRowsAction(
        new_row_indices=[2, 5, 7, 8170, 8171, 8172, 8173], row_data=row_data
    )
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = str(
        Path(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        ).resolve()
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    isa_table_updater = TsvFileUpdater()
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target, file_sha256_hash=sha, actions=[action]
    )
    assert result.success
    assert result.updated_file_sha256_hash

    delete_row_action: TsvDeleteRowsAction = TsvDeleteRowsAction(
        current_row_indices=[8171, 8172]
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=result.updated_file_sha256_hash,
        actions=[delete_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash

    row_data: Dict[int, TsvRowData] = {}
    row = TsvRowData()
    row.values = {2: "Sample X", 3: "Test2"}
    row_data[8170] = row
    row = TsvRowData()
    row.values = {2: "Test 3", 3: "Result"}
    row_data[8171] = row
    update_row_action: TsvActionReport = TsvUpdateRowsAction(rows=row_data)
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=result.updated_file_sha256_hash,
        actions=[update_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_move_row_action_01():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    move_row_action: TsvActionReport = TsvMoveRowAction(
        source_row_index=4, new_row_index=1
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[move_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_move_row_action_02():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    move_row_action: TsvActionReport = TsvMoveRowAction(
        source_row_index=10, new_row_index=0
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[move_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_move_row_action_03():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    move_row_action: TsvActionReport = TsvMoveRowAction(
        source_row_index=2, new_row_index=8166
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[move_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_move_row_action_04():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    move_row_action: TsvActionReport = TsvMoveRowAction(
        source_row_index=8166, new_row_index=20
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[move_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_move_row_action_05():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    move_row_action: TsvActionReport = TsvMoveRowAction(
        source_row_index=20, new_row_index=21
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[move_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_move_row_action_06():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = str(
        Path(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        ).resolve()
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    move_row_action: TsvActionReport = TsvMoveRowAction(
        source_row_index=25, new_row_index=24
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[move_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_move_row_action_07():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    move_row_action: TsvActionReport = TsvMoveRowAction(
        source_row_index=11, new_row_index=11
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[move_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_copy_row_action_01():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    copy_row_action: TsvActionReport = TsvCopyRowAction(
        source_row_index=7, target_row_indices=[0, 1, 2, 3, 4, 5]
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[copy_row_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_add_column_action_01():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    columns: Dict[int, TsvColumnData] = {}
    cell_default_values: Dict[int, str] = {}
    column = TsvColumnData(header_name="Protocol REF", values={})
    cell_default_values[3] = "Extraction"
    columns[3] = column
    add_column_action: TsvActionReport = TsvAddColumnsAction(
        columns=columns, cell_default_values=cell_default_values
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[add_column_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_delete_column_action_01():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    columns: Dict[int, TsvColumnData] = {}
    cell_default_values: Dict[int, str] = {}
    column = TsvColumnData(header_name="Protocol REF", values={})
    cell_default_values[3] = "Extraction"
    columns[3] = column
    delete_column_action: TsvActionReport = TsvDeleteColumnsAction(
        current_columns={1: "Characteristics[Organism]", 7: "Characteristics[Variant]"}
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[delete_column_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_move_column_action_01():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    columns: Dict[int, TsvColumnData] = {}
    cell_default_values: Dict[int, str] = {}
    column = TsvColumnData(header_name="Protocol REF", values={})
    cell_default_values[3] = "Extraction"
    columns[3] = column
    move_column_action: TsvActionReport = TsvMoveColumnAction(
        source_column_index=1,
        source_column_header="Characteristics[Organism]",
        new_column_index=6,
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[move_column_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_copy_column_action_01():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    copy_column_action: TsvActionReport = TsvCopyColumnAction(
        source_column_index=1,
        source_column_header="Characteristics[Organism]",
        target_columns={7: "Characteristics[Variant]", 8: "Term Source REF"},
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[copy_column_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_update_column_header_action_01():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    update_column_header_action: TsvActionReport = TsvUpdateColumnHeaderAction(
        new_headers={7: "Characteristics[Variant].2", 8: "Term Source REF.2"},
    )
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[update_column_header_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_update_column_action_01():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = os.path.realpath(
        os.path.realpath(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        )
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    columns: Dict[int, TsvColumnData] = {}
    column = TsvColumnData(
        header_name="Characteristics[Organism]", values={2: "test 2", 5: "test 5"}
    )
    columns[1] = column
    column = TsvColumnData(
        header_name="Characteristics[Organism part]",
        values={2: "test 2.2", 5: "test 2.5"},
    )
    columns[4] = column
    update_columns_action: TsvActionReport = TsvUpdateColumnsAction(columns=columns)
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[update_columns_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash


def test_update_cells_action_01():
    sha = "add85bc3770cda13450b6fd95fe1735fe6337553076ed7cd269fc8163e002fac"
    isa_table_updater = TsvFileUpdater()
    path_original = str(
        Path(join_path("tests/test-data/test-data-01/s_MTBLS66_test_01.txt")).resolve()
    )
    path_target = str(
        Path(
            join_path("test-temp/test-data/test-data-01/s_MTBLS66_test_01_result.txt")
        ).resolve()
    )
    Path(path_target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path_original, path_target)
    cell1 = TsvCellData(row_index=1, column_index=2, value="Cell Update")
    cell2 = TsvCellData(row_index=2, column_index=1, value="Cell Update2")
    cell3 = TsvCellData(row_index=3, column_index=10, value="Cell Update3")
    cells: List[TsvCellData] = [cell1, cell2, cell3]
    update_cells_action: TsvActionReport = TsvUpdateCellsAction(cells=cells)
    result: TsvActionReport = isa_table_updater.apply_actions(
        file_path=path_target,
        file_sha256_hash=sha,
        actions=[update_cells_action],
    )
    assert result.success
    assert result.updated_file_sha256_hash
