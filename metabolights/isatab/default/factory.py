from metabolights.isatab.default.assay_file import DefaultAssayFileReader
from metabolights.isatab.default.assignment_file import DefaultAssignmentFileReader
from metabolights.isatab.default.investigation_file import (
    DefaultInvestigationFileReader,
    DefaultInvestigationFileWriter,
)
from metabolights.isatab.default.sample_file import DefaultSampleFileReader
from metabolights.isatab.default.writer import DefaultIsaTableFileWriter
from metabolights.isatab.reader import (
    InvestigationFileReader,
    IsaTableFileReader,
    IsaTabReaderFactory,
)
from metabolights.isatab.writer import (
    InvestigationFileWriter,
    IsaTableFileWriter,
    IsaTabWriterFactory,
)


class DefaultIsaTabReaderFactory(IsaTabReaderFactory):
    def get_investigation_file_reader(self) -> InvestigationFileReader:
        return DefaultInvestigationFileReader()

    def get_assay_file_reader(self, results_per_page=100) -> IsaTableFileReader:
        return DefaultAssayFileReader(results_per_page=results_per_page)

    def get_sample_file_reader(self, results_per_page=100) -> IsaTableFileReader:
        return DefaultSampleFileReader(results_per_page=results_per_page)

    def get_assignment_file_reader(self, results_per_page=100) -> IsaTableFileReader:
        return DefaultAssignmentFileReader(results_per_page=results_per_page)


class DefaultIsaTabWriterFactory(IsaTabWriterFactory):
    def get_investigation_file_writer(self) -> InvestigationFileWriter:
        return DefaultInvestigationFileWriter()

    def get_assay_file_writer(self) -> IsaTableFileWriter:
        return DefaultIsaTableFileWriter()

    def get_sample_file_writer(self) -> IsaTableFileWriter:
        return DefaultIsaTableFileWriter()

    def get_assignment_file_writer(self) -> IsaTableFileWriter:
        return DefaultIsaTableFileWriter()
