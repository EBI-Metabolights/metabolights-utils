import os
import pathlib
from abc import ABC, abstractmethod
from io import IOBase
from typing import List, Union

from metabolights_utils.isatab.default.base_isa_file import BaseIsaFile
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.models.isa.common import IsaTable, IsaTableFile
from metabolights_utils.models.isa.parser.isa_table_parser import get_isa_table_file
from metabolights_utils.models.parser.common import ParserMessage, ParserReport
from metabolights_utils.models.parser.enums import ParserMessageType
from metabolights_utils.tsv.filter import TsvFileFilterOption
from metabolights_utils.tsv.sort import TsvFileSortOption
from metabolights_utils.tsv.utils import calculate_sha256


class BaseIsaTableFileReader(BaseIsaFile, IsaTableFileReader, ABC):
    def __init__(self, results_per_page=100) -> None:
        self.results_per_page = results_per_page if results_per_page > 0 else 100

    @abstractmethod
    def get_expected_patterns(self) -> List[List[str]]:
        pass

    def get_total_pages(
        self,
        file_buffer: IOBase = None,
        results_per_page: int = 100,
        file_path: Union[str, pathlib.Path] = None,
    ) -> int:
        buffer_or_path, path = self._get_file_buffer_and_path(file_buffer, file_path)

        total = self.get_total_row_count(buffer_or_path, path)
        return int(total / results_per_page) + (
            1 if total % results_per_page > 0 else 0
        )

    def get_total_row_count(
        self,
        file_buffer: IOBase = None,
        file_path: Union[str, pathlib.Path] = None,
    ) -> int:
        buffer_or_path, path = self._get_file_buffer_and_path(file_buffer, file_path)

        isa_file_result: IsaTableFileReaderResult = self.get_headers(
            buffer_or_path, path
        )
        table_file: IsaTableFile = isa_file_result.isa_table_file
        table: IsaTable = table_file.table
        return table.total_row_count

    def get_page(
        self,
        file_buffer: IOBase = None,
        page: int = 1,
        results_per_page: int = 100,
        selected_columns: Union[List[str], None] = None,
        file_path: Union[str, pathlib.Path] = None,
        filter_options: List[TsvFileFilterOption] = None,
        sort_options: List[TsvFileSortOption] = None,
    ) -> IsaTableFileReaderResult:
        page = page if page and page > 1 else 1
        results_per_page = (
            results_per_page if results_per_page > 0 else self.results_per_page
        )
        offset = (page - 1) * results_per_page
        buffer_or_path, path = self._get_file_buffer_and_path(file_buffer, file_path)
        return self.get_rows(
            file_buffer=buffer_or_path,
            offset=offset,
            limit=results_per_page,
            selected_columns=selected_columns,
            file_path=path,
            filter_options=filter_options,
            sort_options=sort_options,
        )

    def get_rows(
        self,
        file_buffer: IOBase = None,
        file_path: Union[str, pathlib.Path] = None,
        offset: int = 0,
        limit: Union[int, None] = None,
        selected_columns: Union[None, List[str]] = None,
        filter_options: List[TsvFileFilterOption] = None,
        sort_options: List[TsvFileSortOption] = None,
    ) -> IsaTableFileReaderResult:
        offset = offset if offset > 0 else None
        limit = limit if limit is not None and limit >= 0 else None
        selected_columns = selected_columns if selected_columns else None
        buffer_or_path, path = self._get_file_buffer_and_path(file_buffer, file_path)

        return self.read(
            file_path_or_buffer=buffer_or_path,
            file_path=path,
            offset=offset,
            limit=limit,
            selected_columns=selected_columns,
            filter_options=filter_options,
            sort_options=sort_options,
        )

    def get_headers(
        self,
        file_buffer: IOBase = None,
        file_path: Union[str, pathlib.Path] = None,
    ) -> IsaTableFileReaderResult:
        offset = None
        limit = 0
        selected_columns = None
        buffer_or_path, path = self._get_file_buffer_and_path(file_buffer, file_path)

        return self.read(
            file_path_or_buffer=buffer_or_path,
            offset=offset,
            limit=limit,
            selected_columns=selected_columns,
            file_path=path,
            skip_parser_info_messages=True,
        )

    def read(
        self,
        file_path_or_buffer: Union[str, pathlib.Path, IOBase],
        offset: Union[None, int],
        limit: Union[None, int],
        selected_columns: Union[None, List[str]] = None,
        file_path: Union[str, pathlib.Path] = None,
        skip_parser_info_messages: bool = True,
        filter_options: List[TsvFileFilterOption] = None,
        sort_options: List[TsvFileSortOption] = None,
    ) -> IsaTableFileReaderResult:
        buffer: IOBase = None
        read_messages: List[ParserMessage] = []
        try:
            buffer_or_path, path = self._get_file_buffer_and_path(
                file_path_or_buffer, file_path
            )
            basename = os.path.basename(str(path))
            file_buffer = self._get_file_buffer(buffer_or_path)
            isa_table_file: IsaTableFile = get_isa_table_file(
                file_buffer,
                basename,
                messages=read_messages,
                expected_patterns=self.get_expected_patterns(),
                offset=offset,
                limit=limit,
                selected_columns=selected_columns,
                filter_options=filter_options,
                sort_options=sort_options,
            )
            if os.path.exists(file_path):
                isa_table_file.sha256_hash = calculate_sha256(file_path)
            elif os.path.exists(str(file_path_or_buffer)):
                isa_table_file.sha256_hash = calculate_sha256(str(file_path_or_buffer))

        finally:
            self._close_file(buffer, file_path_or_buffer)

        messages = read_messages
        if skip_parser_info_messages:
            messages = [x for x in read_messages if x.type != ParserMessageType.INFO]
        parser_report = ParserReport(messages=messages)
        return IsaTableFileReaderResult(
            isa_table_file=isa_table_file, parser_report=parser_report
        )
