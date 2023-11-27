import pathlib
from abc import ABC
from io import IOBase
from typing import Tuple, Union


class BaseIsaFile(ABC):
    def _get_file_path(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
    ) -> Tuple[Union[str, pathlib.Path, IOBase], str]:
        if not file_buffer_or_path:
            return None
        if isinstance(file_buffer_or_path, IOBase):
            return file_buffer_or_path, file_buffer_or_path.name
        if isinstance(file_buffer_or_path, pathlib.Path):
            return file_buffer_or_path, str(file_buffer_or_path)
        elif isinstance(file_buffer_or_path, str):
            return file_buffer_or_path, file_buffer_or_path

    def _get_file_buffer(
        self, file: Union[str, pathlib.Path, IOBase], encoding="utf-8"
    ) -> IOBase:
        if isinstance(file, IOBase):
            file_buffer = file
        elif isinstance(file, pathlib.Path):
            file_buffer = file.open(mode="r", encoding=encoding)
        elif isinstance(file, str):
            file_buffer = open(file=file, mode="r", encoding=encoding)
        else:
            raise ValueError("file type is not defined")

        return file_buffer

    def _close_file(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
    ):
        # If we opened file, close it
        if (
            not file_buffer_or_path
            and not file_buffer_or_path
            and (
                isinstance(file_buffer_or_path, str)
                or isinstance(file_buffer_or_path, pathlib.Path)
            )
        ):
            file_buffer_or_path.close()
