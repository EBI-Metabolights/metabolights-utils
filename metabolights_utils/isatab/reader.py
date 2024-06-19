import pathlib
from abc import ABC, abstractmethod
from io import IOBase
from typing import List, Union

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.isa.common import IsaTableFile
from metabolights_utils.models.isa.investigation_file import Investigation
from metabolights_utils.models.parser.common import ParserReport
from metabolights_utils.tsv.filter import TsvFileFilterOption
from metabolights_utils.tsv.sort import TsvFileSortOption


class IsaTableFileReaderResult(MetabolightsBaseModel):
    isa_table_file: Annotated[IsaTableFile, Field()] = IsaTableFile()
    parser_report: Annotated[ParserReport, Field()] = ParserReport()


class InvestigationFileReaderResult(MetabolightsBaseModel):
    investigation: Annotated[Investigation, Field()] = Investigation()
    parser_report: Annotated[ParserReport, Field()] = ParserReport()
    file_path: str = ""
    sha256_hash: Union[None, str] = None


class InvestigationFileReader(ABC):
    @abstractmethod
    def read(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
        skip_parser_info_messages: bool = True,
    ) -> InvestigationFileReaderResult:
        """Reads investigation an file and return Investigation model and parser messages.
            If file buffer is not defined, it reads file_path.
           At least one of the file_buffer and file_path parameters should be defined.

        Args:
            file_buffer_or_path (str, pathlib.Path, IOBase): File buffer to read file content.
            io.StringIO, io.TextIOWrapper with open(), etc. Defaults to None.
            file_path (Union[str, pathlib.Path], optional): File path or pathlib.Path object.
            Defaults to None.
            skip_parser_info_messages (bool, optional): clear INFO messages from parser messages.
            Defaults to True.

        Raises:
            exc: any unexpected exception while reading file

        Returns:
            InvestigationFileReaderResult: Investigation model and parser messages
        """


class IsaTableFileReader(ABC):
    @abstractmethod
    def get_headers(
        self, file_buffer_or_path: Union[str, pathlib.Path, IOBase]
    ) -> IsaTableFileReaderResult:
        """_summary_

        Args:
            file_buffer (Union[str, pathlib.Path, IOBase]): File buffer to read file content. io.StringIO, io.TextIOWrapper with open(), etc.
            file_path (Union[str, pathlib.Path], optional): File path or pathlib.Path object.

        Returns:
            IsaTableFileWrapperResult: Returns IsaTableFile without rows and parser messages.
        """

    @abstractmethod
    def get_total_pages(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
        results_per_page: int = 100,
    ) -> int:
        """Returns total number of pages according to results_per_page. At least one of the file_buffer and file_path parameters should be defined.
           If file_buffer is not defined, file_path is not used to read content.
           If file_path is not defined, file path and name will not be added to messages.

        Args:
            file_buffer (Union[str, pathlib.Path, IOBase]): File buffer to read file content. io.StringIO, io.TextIOWrapper with open(), etc.
            results_per_page (int): Items per page. Defaults: 100.

        Returns:
            int: total number of pages in file.
        """

    @abstractmethod
    def get_total_row_count(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
    ) -> int:
        """Returns total number of rows. At least one of the file_buffer and file_path parameters should be defined.
           If file_buffer is not defined, file_path is not used to read content.
           If file_path is not defined, file path and name will not be added to messages.

        Args:
            file_buffer_or_path (str, pathlib.Path, IOBase): File buffer to read file content. io.StringIO, io.TextIOWrapper with open(), etc.
            file_path (Union[str, pathlib.Path], optional): File path or pathlib.Path object.

        Returns:
            int: total number of rows in file. First column is assigned as header row.
        """

    @abstractmethod
    def get_page(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
        page: int = 1,
        results_per_page: int = 100,
        selected_columns: Union[List[str], None] = None,
        filter_options: List[TsvFileFilterOption] = None,
        sort_options: List[TsvFileSortOption] = None,
    ) -> IsaTableFileReaderResult:
        """Reads file and returns the selected page of file. At least one of the file_buffer and file_path parameters should be defined.
           If file_buffer is not defined, file_path is not used to read content.
           If file_path is not defined, file path and name will not be added to messages.

        Args:
            file_buffer_or_path (str, pathlib.Path, IOBase): File buffer to read file content. io.StringIO, io.TextIOWrapper with open(), etc.
            page (int, optional): The page number requested. Defaults to 1.
            results_per_page (int, optional): Number of rows in each page. Defaults to 100.
            selected_columns (Union[List[str], None], optional): Column names will be returned. Returns all columns if it is None. Defaults to None.
            file_path (Union[str, pathlib.Path], optional): File path str or pathlib.Path object
            filter_options (List[TsvFileFilterOption]): filter column names and filter methods. Defaults to None.
            sort_options (List[TsvFileSortOption]): Sort column names. Defaults to None.
        Returns:
            IsaTableFileReaderResult: IsaTableFile model and parser messages
        """

    @abstractmethod
    def get_rows(
        self,
        file_buffer_or_path: Union[str, pathlib.Path, IOBase],
        offset: int = 0,
        limit: Union[int, None] = None,
        selected_columns: Union[None, List[str]] = None,
        filter_options: List[TsvFileFilterOption] = None,
        sort_options: List[TsvFileSortOption] = None,
    ) -> IsaTableFileReaderResult:
        """Reads file and returns rows of the file starting from offset.
           At least one of the file_buffer and file_path parameters should be defined.
           If limit is defined, size of the returned rows will be limited to this value.

        Args:
            file_buffer_or_path (str, pathlib.Path, IOBase): File buffer to read file content. io.StringIO, io.TextIOWrapper with open(), etc.
            offset (int, optional): Starting index of rows will be returned. First rows is header and index of second row is 0. Defaults to 0.
            limit (Union[int, None], optional): Number of rows will be returned. If it is None, return all rows. Defaults to None.
            column_names (Union[List[str], None], optional): Column names will be returned. Returns all columns if it is None. Defaults to None.
            filter_options (List[TsvFileFilterOption]): filter column names and filter methods. Defaults to None.
            sort_options (List[TsvFileSortOption]): Sort column names. Defaults to None.

        Returns:
            IsaTableFileReaderResult: IsaTableFile model and parser messages.
        """

    @abstractmethod
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
        """Reads selected rows with selected columns from tsv file. If sort and filter options are enabled, offset and limit are applied to the final filter and sort result.

        Args:
            file_buffer_or_path (Union[str, pathlib.Path, IOBase]): File buffer or path to read file content. file path str, io.StringIO, io.TextIOWrapper with open(), etc.
            offset (int, optional): Starting index of rows will be returned. First rows is header and index of the second row is 0. Defaults to 0.
            limit (Union[int, None], optional): Number of rows will be returned. If it is None, return all rows. Defaults to 1000.
            selected_columns (Union[List[str], None], optional): Column names will be returned. Returns all columns if it is None. Defaults to None.
            skip_parser_info_messages (bool, optional): clear INFO messages from parser messages. Defaults to True.
            filter_options (List[TsvFileFilterOption]): filter column names and filter methods. Defaults to None.
            sort_options (List[TsvFileSortOption]): Sort column names. Defaults to None.
        Returns:
            IsaTableFileReaderResult: IsaTableFile model and parser messages.
        """


class IsaTabReaderFactory(ABC):
    @abstractmethod
    def get_investigation_file_reader(self) -> InvestigationFileReader:
        pass

    @abstractmethod
    def get_assay_file_reader(self, results_per_page=100) -> IsaTableFileReader:
        pass

    @abstractmethod
    def get_sample_file_reader(self, results_per_page=100) -> IsaTableFileReader:
        pass

    @abstractmethod
    def get_assignment_file_reader(self, results_per_page=100) -> IsaTableFileReader:
        pass
