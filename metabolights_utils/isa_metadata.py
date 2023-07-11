from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from metabolights_utils.models.isa.common import IsaTableFile
from metabolights_utils.models.isa.messages import ParserMessage
from metabolights_utils.models.isa.parser.isa_table_parser import (
    parse_isa_table_sheet_from_fs,
)


class IsaMetadataFileReader(ABC):
    def __init__(self, file_path, items_per_page=100) -> None:
        self.file_path = file_path
        self.items_per_page = items_per_page if items_per_page > 0 else 100

    def get_total_row_count(self):
        isa_file, _ = self.get_file_headers()
        return isa_file.table.totalRowCount

    def get_total_pages(self, items_per_page: int = 100):
        total = self.get_total_row_count()
        return int(total / items_per_page) + (1 if total % items_per_page > 0 else 0)

    def get_page(
        self,
        page: int = 1,
        items_per_page: int = 100,
        column_names: Union[List[str], None] = None,
    ):
        page = page if page and page > 1 else 1
        items_per_page = items_per_page if items_per_page > 0 else self.items_per_page
        row_offset = (page - 1) * items_per_page
        return self.get_file_rows(
            row_offset=row_offset,
            number_of_rows=items_per_page,
            column_names=column_names,
        )

    def get_file_headers(self) -> Tuple[IsaTableFile, List[ParserMessage]]:
        skiprows = None
        nrows = 0
        usecols = None
        table, messages = parse_isa_table_sheet_from_fs(
            self.file_path,
            expected_patterns=self.get_expected_patterns(),
            skiprows=skiprows,
            nrows=nrows,
            usecols=usecols,
        )
        return table, messages

    @abstractmethod
    def get_expected_patterns(self) -> List[List[str]]:
        pass

    def get_file_rows(
        self,
        row_offset: int = 0,
        number_of_rows: int = -1,
        column_names: Union[None, List[str]] = None,
    ) -> Tuple[IsaTableFile, List[ParserMessage]]:
        skiprows = range(1, row_offset + 1) if row_offset > 0 else None
        nrows = number_of_rows if number_of_rows >= 0 else None
        usecols = column_names if column_names else None
        table, messages = parse_isa_table_sheet_from_fs(
            self.file_path,
            expected_patterns=self.get_expected_patterns(),
            skiprows=skiprows,
            nrows=nrows,
            usecols=usecols,
        )
        return table, messages


class SampleFileReader(IsaMetadataFileReader):
    patterns = [
        ["^(Source Name)$", ""],
        ["^Characteristics\[(\w[ -~]*)\]$", "Characteristics"],
        ["^(Protocol REF)(\.\d+)?$", "Protocol"],
        ["^(Sample Name)$", ""],
        ["^Factor Value\[(\w[ -~]*)\]$", "Factor Value"],
        ["^Comment\b\[(\w{1}[ -~]*)\]$", "Comment"],
    ]

    def __init__(self, file_path) -> None:
        super().__init__(file_path)

    def get_expected_patterns(self) -> List[List[str]]:
        return SampleFileReader.patterns


class AssayFileReader(IsaMetadataFileReader):
    patterns = [
        ["^(Extract Name)$", ""],
        ["^(Protocol REF)(\.\d+)?$", "Protocol"],
        ["^(Sample Name)$", ""],
        ["^Parameter Value\[(\w[ -~]*)\]$", "Parameter Value"],
        ["^Comment\b\[(\w{1}[ -~]*)\]$", "Comment"],
        ["^(Labeled Extract Name)$", ""],
        ["^(Label)$", ""],
    ]

    def __init__(self, file_path) -> None:
        super().__init__(file_path)

    def get_expected_patterns(self) -> List[List[str]]:
        return AssayFileReader.patterns


class AssignmentFileReader(IsaMetadataFileReader):
    patterns = [
        ["^(datdatabase_identifier)$", ""],
        ["^(chemical_formula)$", ""],
        ["^(smiles)$", ""],
        ["^(inchi)$", ""],
        ["^(metabolite_identification)$", ""],
        ["^(mass_to_charge)$", ""],
        ["^(fragmentation)$", ""],
        ["^(modifications)$", ""],
        ["^(charge)$", ""],
        ["^(retention_time)$", ""],
        ["^(taxid)$", ""],
        ["^(chemical_shift)$", ""],
        ["^(multiplicity)$", ""],
        ["^(species)$", ""],
        ["^(database)$", ""],
        ["^(database_version)$", ""],
        ["^(reliability)$", ""],
        ["^(uri)$", ""],
        ["^(search_engine)$", ""],
        ["^(search_engine_score)$", ""],
        ["^(smallmolecule_abundance_sub)$", ""],
        ["^(smallmolecule_abundance_stdev_sub)$", ""],
        ["^(smallmolecule_abundance_std_error_sub)$", ""],
    ]

    def __init__(self, file_path) -> None:
        super().__init__(file_path)

    def get_expected_patterns(self) -> List[List[str]]:
        return AssignmentFileReader.patterns
