import pathlib
from typing import Dict, Union

from metabolights_utils.isatab.writer import IsaTableFileWriter
from metabolights_utils.models.isa.common import IsaTable
from metabolights_utils.tsv.model import (
    TsvActionReport,
    TsvColumnData,
    TsvUpdateColumnsAction,
)
from metabolights_utils.tsv.tsv_file_updater import TsvFileUpdater


class DefaultIsaTableFileWriter(TsvFileUpdater, IsaTableFileWriter):
    def save_isa_table(
        self,
        file_path: Union[str, pathlib.Path],
        file_sha256_hash: str,
        isa_table: IsaTable,
    ) -> TsvActionReport:
        column_indices = dict(zip(isa_table.columns, isa_table.column_indices))
        headers = {
            column_indices[x.column_header]: x.column_header for x in isa_table.headers
        }

        columns: Dict[int, TsvColumnData] = {}
        for column_name in isa_table.data:
            column_data: TsvColumnData = TsvColumnData()
            column_index = column_indices[column_name]
            columns[column_index] = column_data
            column_data.header_name = headers[column_index]
            column_data.values = dict(
                zip(isa_table.row_indices, isa_table.data[column_name])
            )

        column_update_action = TsvUpdateColumnsAction(columns=columns)
        report = self.apply_actions(
            file_path=file_path,
            file_sha256_hash=file_sha256_hash,
            actions=[column_update_action],
        )
        return report
