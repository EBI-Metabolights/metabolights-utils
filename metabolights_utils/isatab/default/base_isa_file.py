import os
import pathlib
from abc import ABC
from io import IOBase
from typing import Union


class BaseIsaFile(ABC):
    def _get_file_buffer_and_path(
        self,
        file_buffer: IOBase = None,
        file_path: Union[str, pathlib.Path] = None,
    ) -> int:
        if not file_buffer and not file_path:
            ValueError("At least file buffer or file path should be defined")

        selected_file_buffer = (
            file_path if file_path and not file_buffer else file_buffer
        )
        selected_file_path = file_path if file_path else "<processed content>"
        return selected_file_buffer, selected_file_path

    def _get_file_buffer(self, file: Union[str, pathlib.Path, IOBase]) -> IOBase:
        if isinstance(file, IOBase):
            file_buffer = file
        elif isinstance(file, pathlib.Path):
            file_buffer = file.open()
        elif isinstance(file, str):
            file_buffer = open(file=file, mode="r")
        else:
            raise ValueError("file type is not defined")

        return file_buffer

    def _close_file(
        self,
        file_buffer_or_path: IOBase,
        file_path_or_buffer: Union[str, pathlib.Path, IOBase],
    ):
        # If we opened file, close it
        if (
            not file_buffer_or_path
            and not file_path_or_buffer
            and (
                isinstance(file_path_or_buffer, str)
                or isinstance(file_buffer_or_path, pathlib.Path)
            )
        ):
            file_buffer_or_path.close()
