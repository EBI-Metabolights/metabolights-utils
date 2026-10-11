import logging
import os
import pathlib
from contextlib import contextmanager
from io import BytesIO, IOBase, TextIOWrapper
from typing import Generator, Tuple, Union

logger = logging.getLogger(__name__)


class BaseIsaFile:
    def _get_file_path(
        self,
        file_buffer_or_path: Union[str, bytes, pathlib.Path, IOBase],
        filename: Union[str, None] = None,
    ) -> Tuple[Union[str, pathlib.Path, IOBase], str]:
        if not file_buffer_or_path:
            logger.warning("file_buffer_or_path input is not defined.")
            return None
        if isinstance(file_buffer_or_path, bytes):
            file_buffer_or_path = BytesIO(file_buffer_or_path)
        if isinstance(file_buffer_or_path, IOBase):
            if hasattr(file_buffer_or_path, "name"):
                return file_buffer_or_path, os.path.realpath(file_buffer_or_path.name)
            return file_buffer_or_path, os.path.realpath(filename) if filename else ""
        if isinstance(file_buffer_or_path, pathlib.Path):
            return file_buffer_or_path, os.path.realpath(str(file_buffer_or_path))
        elif isinstance(file_buffer_or_path, str):
            return file_buffer_or_path, os.path.realpath(file_buffer_or_path)

    @contextmanager
    def _get_file_buffer(
        self, file: Union[str, pathlib.Path, IOBase], encoding="utf-8"
    ) -> Generator[IOBase, None, None]:
        if isinstance(file, IOBase):
            # The caller owns streams passed directly to the reader.
            yield file
        elif isinstance(file, (pathlib.Path, str)):
            with self.open_file(file=file, encoding=encoding) as file_buffer:
                yield file_buffer
        else:
            logger.error("Input type is not valid: %s.", type(file))
            raise TypeError("file type is not defined")

    @contextmanager
    def open_file(
        self, file: pathlib.Path | str, encoding: str
    ) -> Generator[TextIOWrapper, None, None]:
        if isinstance(file, str):
            file = pathlib.Path(file)
        try:
            with file.open(mode="r", encoding=encoding) as text_io:
                yield text_io
        finally:
            logger.debug("File %s is closed.", file)
