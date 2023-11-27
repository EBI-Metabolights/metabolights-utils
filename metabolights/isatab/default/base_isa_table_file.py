import os
import pathlib
from abc import ABC, abstractmethod
from io import IOBase
from typing import List, Union

from metabolights.isatab.default.base_isa_file import BaseIsaFile
from metabolights.isatab.default.parser.isa_table_parser import get_isa_table_file
from metabolights.isatab.reader import IsaTableFileReader, IsaTableFileReaderResult
from metabolights.models.isa.common import IsaTable, IsaTableFile
from metabolights.models.parser.common import ParserMessage, ParserReport
from metabolights.models.parser.enums import ParserMessageType
from metabolights.tsv.filter import TsvFileFilterOption
from metabolights.tsv.sort import TsvFileSortOption
from metabolights.tsv.utils import calculate_sha256


class BaseIsaTableFileReader(BaseIsaFile, IsaTableFileReader, ABC):
    def __init__(self, results_per_page=100) -> None:
        self.results_per_page = results_per_page if results_per_page > 0 else 100

    @abstractmethod
    def get_expected_patterns(self) -> List[List[str]]:
        pass

    def get_total_pages(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
        results_per_page: int = 100,
    ) -> int:
        total = self.get_total_row_count(file_buffer_or_path)
        return int(total / results_per_page) + (
            1 if total % results_per_page > 0 else 0
        )

    def get_total_row_count(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
    ) -> int:
        isa_file_result: IsaTableFileReaderResult = self.get_headers(
            file_buffer_or_path
        )
        table_file: IsaTableFile = isa_file_result.isa_table_file
        table: IsaTable = table_file.table
        return table.total_row_count

    def get_page(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
        page: int = 1,
        results_per_page: int = 100,
        selected_columns: Union[List[str], None] = None,
        filter_options: List[TsvFileFilterOption] = None,
        sort_options: List[TsvFileSortOption] = None,
    ) -> IsaTableFileReaderResult:
        page = page if page and page > 1 else 1
        results_per_page = (
            results_per_page if results_per_page > 0 else self.results_per_page
        )
        offset = (page - 1) * results_per_page
        return self.get_rows(
            file_buffer_or_path=file_buffer_or_path,
            offset=offset,
            limit=results_per_page,
            selected_columns=selected_columns,
            filter_options=filter_options,
            sort_options=sort_options,
        )

    def get_rows(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
        offset: int = 0,
        limit: Union[int, None] = None,
        selected_columns: Union[None, List[str]] = None,
        filter_options: List[TsvFileFilterOption] = None,
        sort_options: List[TsvFileSortOption] = None,
    ) -> IsaTableFileReaderResult:
        offset = offset if offset > 0 else None
        limit = limit if limit is not None and limit >= 0 else None
        selected_columns = selected_columns if selected_columns else None

        return self.read(
            file_buffer_or_path=file_buffer_or_path,
            offset=offset,
            limit=limit,
            selected_columns=selected_columns,
            filter_options=filter_options,
            sort_options=sort_options,
        )

    def get_headers(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
    ) -> IsaTableFileReaderResult:
        offset = None
        limit = 0
        selected_columns = None

        return self.read(
            file_buffer_or_path=file_buffer_or_path,
            offset=offset,
            limit=limit,
            selected_columns=selected_columns,
            skip_parser_info_messages=True,
        )

    def read(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
        offset: Union[None, int],
        limit: Union[None, int],
        selected_columns: Union[None, List[str]] = None,
        skip_parser_info_messages: bool = True,
        filter_options: List[TsvFileFilterOption] = None,
        sort_options: List[TsvFileSortOption] = None,
    ) -> IsaTableFileReaderResult:
        buffer: IOBase = None
        read_messages: List[ParserMessage] = []
        try:
            buffer_or_path, path = self._get_file_path(file_buffer_or_path)
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
            if os.path.exists(path):
                isa_table_file.sha256_hash = calculate_sha256(path)
            elif os.path.exists(str(file_buffer_or_path)):
                isa_table_file.sha256_hash = calculate_sha256(str(file_buffer_or_path))

        finally:
            self._close_file(file_buffer_or_path)

        messages = read_messages
        if skip_parser_info_messages:
            messages = [x for x in read_messages if x.type != ParserMessageType.INFO]
        parser_report = ParserReport(messages=messages)
        return IsaTableFileReaderResult(
            isa_table_file=isa_table_file, parser_report=parser_report
        )
