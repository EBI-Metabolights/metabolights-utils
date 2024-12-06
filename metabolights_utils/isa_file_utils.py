import logging
import os
from typing import Any, Union

from metabolights_utils.isatab import Writer
from metabolights_utils.models.isa.common import IsaTableFile
from metabolights_utils.models.metabolights.model import MetabolightsStudyModel

logger = logging.getLogger(__name__)


class IsaFileUtils:

    @staticmethod
    async def save_metabolights_study_model(
        mtbls_model: MetabolightsStudyModel,
        output_dir: str,
        values_in_quotation_mark: bool = False,
        investigation_module_name: Union[None, str] = None,
    ):
        if not os.path.exists(output_dir):
            logger.info(f"Study save folder % is created", output_dir)
            os.makedirs(output_dir, exist_ok=True)
        i_file_name = mtbls_model.investigation_file_path
        logger.info("Saving investigation file: %s", i_file_name)
        Writer.get_investigation_file_writer().write(
            mtbls_model.investigation,
            f"{output_dir}/{mtbls_model.investigation_file_path}",
            values_in_quotation_mark=values_in_quotation_mark,
            investigation_module_name=investigation_module_name,
        )
        for isa_table_files in (
            mtbls_model.samples,
            mtbls_model.assays,
            mtbls_model.metabolite_assignments,
        ):
            for isa_table_file in isa_table_files.values():
                i_file_name = isa_table_file.file_path
                await IsaFileUtils.save_isa_table(
                    isa_table_file,
                    f"{output_dir}/{isa_table_file.file_path}",
                    values_in_quotation_mark=values_in_quotation_mark,
                )

    @staticmethod
    def sanitise_data(self, value: Union[None, Any]):
        if isinstance(value, list):
            for idx, val in enumerate(value):
                value[idx] = IsaFileUtils.sanitise_single_value(val)
            return value
        return IsaFileUtils.sanitise_single_value(value)

    @staticmethod
    def sanitise_single_value(self, value: Union[None, Any]):
        if value is None:
            return ""
        return (
            str(value).replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()
        )

    @staticmethod
    async def save_isa_table(
        isa_table_file: IsaTableFile,
        file_path: str,
        values_in_quotation_mark=False,
    ):
        column_order_map = {}
        column_header_map = {}
        data = isa_table_file.table.data
        for column_model in isa_table_file.table.headers:
            column_order_map[column_model.column_index] = column_model.column_name
            column_header_map[column_model.column_index] = column_model.column_header
        parent_dir = os.path.dirname(file_path)
        basename = os.path.dirname(file_path)
        if not os.path.exists(parent_dir):
            logger.info(f"Study save folder % is created", parent_dir)
            os.makedirs(parent_dir, exist_ok=True)

        logger.info("Saving file: %s", basename)
        with open(file_path, "w") as f:
            if values_in_quotation_mark:
                header = [
                    f'"{column_header_map[idx]}"'
                    for idx in range(len(column_header_map))
                ]
            else:
                header = [
                    column_header_map[idx].strip('"')
                    for idx in range(len(column_header_map))
                ]
            f.write("\t".join(header) + "\n")

            column_names = [
                column_order_map[idx] for idx in range(len(column_order_map))
            ]
            for row_idx in range(len(data[column_names[0]])):
                row = [data[column_name][row_idx] for column_name in column_names]
                for idx, cell in enumerate(row):
                    cell = IsaFileUtils.sanitise_data(cell) if row[idx] else ""
                    if values_in_quotation_mark:
                        cell = f'"{cell}"'
                    else:
                        cell = cell.strip('"')
                    row[idx] = cell
                f.write("\t".join(row) + "\n")
