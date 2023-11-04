import os
import pathlib
import shutil
from abc import ABC, abstractmethod
from io import IOBase
from typing import List

from metabolights_utils.tsv import model as actions


class TsvActionException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class BaseTsvAction(ABC):
    @abstractmethod
    def apply_action(
        self,
        source_file_path: pathlib.Path,
        target_file_path: pathlib.Path,
        action: actions.TsvAction,
    ) -> actions.TsvActionResult:
        pass

    def delete_file(self, path):
        if os.path.exists(path):
            if os.path.islink(path):
                os.unlink(path)
            elif os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

    def get_updated_row(self, empty_row, input_row: actions.TsvRowData):
        column_indices = range(len(empty_row))
        data_values = input_row.values

        merge = (
            lambda x: data_values[x]
            if data_values and x in data_values
            else empty_row[x]
        )
        map_result = map(merge, column_indices)
        return list(map_result)

    def write_row(self, file_buffer: IOBase, row: List[str]):
        new_row_string = "\t".join(row) + "\n"
        file_buffer.write(new_row_string)
