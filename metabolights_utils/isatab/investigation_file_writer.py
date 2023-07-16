import pathlib
from abc import ABC, abstractmethod
from io import IOBase
from typing import Union

from pydantic import Field

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.isa.investigation_file import Investigation
from metabolights_utils.models.parser.common import ParserReport


class InvestigationFileReaderResult(MetabolightsBaseModel):
    investigation: Investigation = Field(Investigation())
    parser_report: ParserReport = Field(ParserReport())


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
    ):
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
