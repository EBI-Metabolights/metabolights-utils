import pathlib
import shutil
from abc import ABC, abstractmethod
from io import IOBase
from typing import List

from metabolights_utils.tsv import model as actions


class TsvActionException(Exception):
    def __init__(self, message: str = "") -> None:
        self.message = message


class BaseTsvAction(ABC):
    @abstractmethod
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvAction,
        read_encoding: str = "utf-8",
        write_encoding: str = "utf-8",
    ) -> actions.TsvActionResult:
        pass

    def delete_file(self, file_path: str):
        file = pathlib.Path(file_path)
        if file.exists():
            if file.is_dir():
                shutil.rmtree(file)
            else:
                file.unlink()

    def get_updated_row(self, empty_row, input_row: actions.TsvRowData):
        column_indices = range(len(empty_row))
        data_values = input_row.values

        def merge_method(x):
            return data_values[x] if data_values and x in data_values else empty_row[x]

        map_result = map(merge_method, column_indices)
        return list(map_result)

    def write_row(self, file_buffer: IOBase, row: List[str]):
        new_row_string = "\t".join(row) + "\n"
        file_buffer.write(new_row_string)
