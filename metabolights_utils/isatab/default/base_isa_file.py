import logging
import os
import pathlib
from io import IOBase
from typing import Tuple, Union

logger = logging.getLogger(__name__)


class BaseIsaFile:
    def _get_file_path(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
    ) -> Tuple[Union[str, pathlib.Path, IOBase], str]:
        if not file_buffer_or_path:
            logger.warning("file_buffer_or_path input is not defined.")
            return None
        if isinstance(file_buffer_or_path, IOBase):
            return file_buffer_or_path, os.path.realpath(file_buffer_or_path.name)
        if isinstance(file_buffer_or_path, pathlib.Path):
            return file_buffer_or_path, os.path.realpath(str(file_buffer_or_path))
        elif isinstance(file_buffer_or_path, str):
            return file_buffer_or_path, os.path.realpath(file_buffer_or_path)

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
            logger.error("Input type is not valid: %s.", type(file))
            raise ValueError("file type is not defined")

        return file_buffer

    def _close_file(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
    ):
        # If we opened file, close it
        if file_buffer_or_path and isinstance(file_buffer_or_path, IOBase):
            file_buffer_or_path.close()
