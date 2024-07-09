import logging

from metabolights_utils.isatab.default.assay_file import DefaultAssayFileReader
from metabolights_utils.isatab.default.assignment_file import (
    DefaultAssignmentFileReader,
)
from metabolights_utils.isatab.default.investigation_file import (
    DefaultInvestigationFileReader,
    DefaultInvestigationFileWriter,
)
from metabolights_utils.isatab.default.sample_file import DefaultSampleFileReader
from metabolights_utils.isatab.default.writer import DefaultIsaTableFileWriter
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    IsaTableFileReader,
    IsaTabReaderFactory,
)
from metabolights_utils.isatab.writer import (
    InvestigationFileWriter,
    IsaTableFileWriter,
    IsaTabWriterFactory,
)

logger = logging.getLogger(__name__)


class DefaultIsaTabReaderFactory(IsaTabReaderFactory):
    def get_investigation_file_reader(self) -> InvestigationFileReader:
        logger.debug("Return default investigation file reader.")
        return DefaultInvestigationFileReader()

    def get_assay_file_reader(self, results_per_page=100) -> IsaTableFileReader:
        logger.debug("Return default assay file reader.")
        return DefaultAssayFileReader(results_per_page=results_per_page)

    def get_sample_file_reader(self, results_per_page=100) -> IsaTableFileReader:
        logger.debug("Return default sample file reader.")
        return DefaultSampleFileReader(results_per_page=results_per_page)

    def get_assignment_file_reader(self, results_per_page=100) -> IsaTableFileReader:
        logger.debug("Return default maf file reader.")
        return DefaultAssignmentFileReader(results_per_page=results_per_page)


class DefaultIsaTabWriterFactory(IsaTabWriterFactory):
    def get_investigation_file_writer(self) -> InvestigationFileWriter:
        logger.debug("Return default investigation file writer.")
        return DefaultInvestigationFileWriter()

    def get_assay_file_writer(self) -> IsaTableFileWriter:
        logger.debug("Return default ISA table file writer for assay file.")
        return DefaultIsaTableFileWriter()

    def get_sample_file_writer(self) -> IsaTableFileWriter:
        logger.debug("Return default ISA table file writer for sample file.")
        return DefaultIsaTableFileWriter()

    def get_assignment_file_writer(self) -> IsaTableFileWriter:
        logger.debug("Return default ISA table file writer for maf file.")
        return DefaultIsaTableFileWriter()
