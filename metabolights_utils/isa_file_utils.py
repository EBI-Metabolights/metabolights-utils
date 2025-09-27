import logging
from pathlib import Path
from typing import Any, List, Tuple, Union

from metabolights_utils.isatab import Writer
from metabolights_utils.models.isa.common import IsaTable, IsaTableColumn, IsaTableFile
from metabolights_utils.models.isa.enums import ColumnsStructure
from metabolights_utils.models.metabolights.model import MetabolightsStudyModel

logger = logging.getLogger(__name__)


class IsaFileUtils:
    @staticmethod
    async def save_metabolights_study_model(
        mtbls_model: MetabolightsStudyModel,
        output_dir: str,
        values_in_quotation_mark: bool = False,
        investigation_module_name: Union[None, str] = None,
        sync_comments_from_fields: bool = True,
    ):
        output_dir_path = Path(output_dir)
        if not output_dir_path.exists():
            logger.info("Study save folder %s is created", output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)

        i_file_name = mtbls_model.investigation_file_path
        logger.info("Saving investigation file: %s", i_file_name)
        Writer.get_investigation_file_writer().write(
            mtbls_model.investigation,
            f"{output_dir}/{mtbls_model.investigation_file_path}",
            values_in_quotation_mark=values_in_quotation_mark,
            investigation_module_name=investigation_module_name,
            sync_comments_from_fields=sync_comments_from_fields,
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
    def sanitise_data(value: Union[None, Any]):
        if isinstance(value, list):
            for idx, val in enumerate(value):
                value[idx] = IsaFileUtils.sanitise_single_value(val)
            return value
        return IsaFileUtils.sanitise_single_value(value)

    @staticmethod
    def sanitise_single_value(value: Union[None, Any]):
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
        file = Path(file_path)
        basename = file.parent.name
        if not file.parent.exists():
            logger.info("Study save folder %s is created", file.parent)
            file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Saving file: %s", basename)
        with file.open("w") as f:
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

    @staticmethod
    def add_isa_table_columns(
        mtbls_isa_table: IsaTable,
        header_name: str,
        new_column_index: Union[int, None] = None,
        column_structure: ColumnsStructure = ColumnsStructure.ONTOLOGY_COLUMN,
        default_value: Union[str, None] = None,
    ) -> Tuple[List[str], int]:
        if column_structure not in (
            ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY,
            ColumnsStructure.ONTOLOGY_COLUMN,
            ColumnsStructure.SINGLE_COLUMN,
        ):
            raise ValueError(
                f"Column structure {column_structure.value} is not valid. "
            )
        table_columns = mtbls_isa_table.columns
        headers = mtbls_isa_table.headers
        selected_index = len(table_columns)
        if (
            new_column_index is not None
            and new_column_index >= 0
            and len(table_columns) >= new_column_index
        ):
            selected_index = new_column_index
        search_headers = [header_name]
        new_column_names = []
        linked_column_names = []
        if column_structure == ColumnsStructure.SINGLE_COLUMN_AND_UNIT_ONTOLOGY:
            linked_column_names = ["Unit", "Term Source REF", "Term Accession Number"]
        elif column_structure == ColumnsStructure.ONTOLOGY_COLUMN:
            linked_column_names = ["Term Source REF", "Term Accession Number"]
        elif column_structure == ColumnsStructure.SINGLE_COLUMN:
            linked_column_names = []

        search_headers.extend(linked_column_names)

        default_value = default_value if default_value else ""
        new_columns = []

        for item in search_headers:
            count = sum([1 for x in headers if x.column_header == item])
            new_column_name = f"{item}.{(count)}" if count > 0 else item
            new_column_names.append(new_column_name)

            if item == header_name:
                categories = header_name.split("[")
                category = ""
                if len(categories) > 1:
                    category = categories[0]
                column_model = IsaTableColumn(
                    column_index=selected_index,
                    column_header=item,
                    column_name=new_column_name,
                    column_category=category,
                    column_prefix=category,
                    additional_columns=linked_column_names,
                    default_value=default_value,
                    column_structure=column_structure,
                )
            else:
                column_model = IsaTableColumn(
                    column_index=selected_index,
                    column_header=item,
                    column_name=new_column_name,
                    column_category="",
                    column_prefix="",
                    column_structure=ColumnsStructure.LINKED_COLUMN,
                )

            new_columns.append(column_model)
            mtbls_isa_table.data[new_column_name] = []
            if mtbls_isa_table.columns and mtbls_isa_table.data:
                first_column_data = mtbls_isa_table.data[mtbls_isa_table.columns[0]]
                mtbls_isa_table.data[new_column_name] = [""] * len(first_column_data)

        if selected_index == len(table_columns):
            updated_header_models = headers + new_columns
            updated_columns = table_columns + new_column_names
        else:
            updated_header_models = (
                headers[:selected_index] + new_columns + headers[selected_index:]
            )

            updated_columns = (
                table_columns[:selected_index]
                + new_column_names
                + table_columns[selected_index:]
            )

        for idx, val in enumerate(updated_columns):
            if idx >= len(table_columns):
                table_columns.append(val)
                headers.append(updated_header_models[idx])
                headers[idx].column_index = idx
            else:
                table_columns[idx] = val
                headers[idx] = updated_header_models[idx]
                headers[idx].column_index = idx
        mtbls_isa_table.column_indices = [x for x in range(len(table_columns))]

        return new_column_names, selected_index
