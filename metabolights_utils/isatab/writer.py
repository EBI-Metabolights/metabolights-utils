import pathlib
from abc import ABC, abstractmethod
from io import IOBase
from typing import List, Union

from metabolights_utils.isatab.reader import InvestigationFileReaderResult
from metabolights_utils.models.isa.common import IsaTable
from metabolights_utils.models.isa.investigation_file import Investigation
from metabolights_utils.tsv.model import TsvAction, TsvActionReport


class InvestigationFileWriter(ABC):
    @abstractmethod
    def write(
        self,
        investigation: Investigation,
        file_buffer: IOBase = None,
        file_path: Union[str, pathlib.Path] = None,
        values_in_quatation_mark: bool = True,
        verify_file_after_update: bool = True,
        skip_parser_info_messages: bool = True,
    ) -> InvestigationFileReaderResult:
        """Converts investigation file model to isatab inverstigation format and writes to file buffer.
           If file buffer is not defined, it creates/updates a file on file_path.
           At least one of the file_buffer and file_path parameters should be defined.

        Args:
            investigation (Investigation): investigation file object.
            file_buffer (IOBase): File buffer to read file content. io.StringIO, io.TextIOWrapper with open(), etc.
            file_path (Union[str, pathlib.Path], optional): File path or pathlib.Path object.
            values_in_quatation_mark (bool, optional): add values in quatation_mark. Defaults to True.
            verify_file_after_update (bool, optional): Reads investigation file if it is True. Defaults to True.
            skip_parser_info_messages (bool, optional): clear INFO messages from parser messages. Defaults to True.
        Returns:
            InvestigationFileReaderResult: Returns updated investigation model and parser messages if verify_file_after_update is True.
                If verify_file_after_update is False, return input investigation and empty parser message report
        """


class IsaTableFileWriter(ABC):
    @abstractmethod
    def apply_actions(
        self,
        file_path: Union[str, pathlib.Path],
        file_sha256_hash: str,
        actions: List[TsvAction],
    ) -> TsvActionReport:
        """Applies

        Args:
            file_path (Union[str, pathlib.Path], optional): File path or pathlib.Path object.
            file_sha256_hash (str): SH256 of the input file. If file SHA256 does not match, method returns error.
            actions (List[TsvAction]): List of allowed actions
        Returns:
            TsvActionReport: results of each action. If an action result is not success, result message will be available.
        """

    @abstractmethod
    def save_isa_table(
        self,
        file_path: Union[str, pathlib.Path],
        file_sha256_hash: str,
        isa_table: IsaTable,
    ) -> TsvActionReport:
        """Applies

        Args:
            file_path (Union[str, pathlib.Path], optional): File path or pathlib.Path object.
            file_sha256_hash (str): SH256 of the input file. If file SHA256 does not match, method returns error.
            actions (List[TsvAction]): List of allowed actions
        Returns:
            TsvActionReport: results of each action. If an action result is not success, result message will be available.
        """


class IsaTabWriterFactory(ABC):
    @abstractmethod
    def get_investigation_file_writer() -> InvestigationFileWriter:
        pass

    @abstractmethod
    def get_assay_file_writer() -> IsaTableFileWriter:
        pass

    @abstractmethod
    def get_sample_file_writer() -> IsaTableFileWriter:
        pass

    @abstractmethod
    def get_assignment_file_writer() -> IsaTableFileWriter:
        pass
