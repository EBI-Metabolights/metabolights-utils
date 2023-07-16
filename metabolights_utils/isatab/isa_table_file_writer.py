import pathlib
from abc import ABC, abstractmethod
from io import IOBase
from typing import List, Union

from metabolights_utils.isatab.isa_table_file_reader import IsaTableFileReaderResult
from metabolights_utils.models.isa.common import IsaTableFile


class IsaTableFileWriterResult(IsaTableFileReaderResult):
    pass


class IsaTableFileWriter(ABC):
    @abstractmethod
    def add_columns(column_names: List[str], column_offset: int):
        pass

    @abstractmethod
    def add_rows(
        self,
        source: IsaTableFile,
        target: Union[str, pathlib.Path, IOBase, IsaTableFile],
        source_offset: int,
        target_offset: Union[None, int],
        limit: Union[None, int],
        column_names: Union[None, List[str]] = None,
        file_path: Union[str, pathlib.Path] = None,
        skip_parser_info_messages: bool = True,
    ) -> IsaTableFileWriterResult:
        pass

    @abstractmethod
    def update_rows(
        self,
        source: IsaTableFile,
        target: Union[str, pathlib.Path, IOBase],
        source_offset: int,
        target_offset: Union[None, int],
        limit: Union[None, int],
        column_names: Union[None, List[str]] = None,
        file_path: Union[str, pathlib.Path] = None,
        skip_parser_info_messages: bool = True,
    ) -> IsaTableFileWriterResult:
        """_summary_

        Args:
            file_path_or_buffer (Union[str, pathlib.Path, IOBase]): File buffer or path to read file content.
            file path str, io.StringIO, io.TextIOWrapper with open(), etc.
            offset (int, optional): Starting index of rows will be returned. First rows is header and index of second row is 0. Defaults to 0.
            limit (Union[int, None], optional): Number of rows will be returned. If it is None, return all rows. Defaults to None.
            column_names (Union[List[str], None], optional): Column names will be returned. Returns all columns if it is None. Defaults to None.
            file_path (Union[str, pathlib.Path], optional): File path str or pathlib.Path object
            skip_parser_info_messages (bool, optional): clear INFO messages from parser messages. Defaults to True.

        Returns:
            IsaTableFileParserResult: IsaTableFile model and parser messages.
        """
        pass
