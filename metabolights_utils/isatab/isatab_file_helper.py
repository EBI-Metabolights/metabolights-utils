from metabolights_utils.isatab.helper.assay_file_helper import AssayFileHelper
from metabolights_utils.isatab.helper.assignment_file_helper import AssignmentFileHelper
from metabolights_utils.isatab.helper.investigation_file_helper import InvestigationFileHelper
from metabolights_utils.isatab.helper.sample_file_helper import SampleFileHelper
from metabolights_utils.isatab.investigation_file_reader import InvestigationFileReader
from metabolights_utils.isatab.investigation_file_writer import InvestigationFileWriter
from metabolights_utils.isatab.isa_table_file_reader import IsaTableFileReader
from metabolights_utils.isatab.isa_table_file_writer import IsaTableFileWriter


class IsaTabFileHelper(object):
    @staticmethod
    def get_investigation_file_reader() -> InvestigationFileReader:
        return InvestigationFileHelper()

    @staticmethod
    def get_investigation_file_writer() -> InvestigationFileWriter:
        return InvestigationFileHelper()

    @staticmethod
    def get_assay_file_reader(results_per_page=100) -> IsaTableFileReader:
        return AssayFileHelper(results_per_page=results_per_page)

    @staticmethod
    def get_assay_file_writer(results_per_page=100) -> IsaTableFileWriter:
        return AssayFileHelper(results_per_page=results_per_page)

    @staticmethod
    def get_sample_file_reader(results_per_page=100) -> IsaTableFileReader:
        return SampleFileHelper(results_per_page=results_per_page)

    @staticmethod
    def get_sample_file_writer(results_per_page=100) -> IsaTableFileWriter:
        return SampleFileHelper(results_per_page=results_per_page)

    @staticmethod
    def get_assignment_file_reader(results_per_page=100) -> IsaTableFileReader:
        return AssignmentFileHelper(results_per_page=results_per_page)

    @staticmethod
    def get_assignment_file_writer(results_per_page=100) -> IsaTableFileWriter:
        return AssignmentFileHelper(results_per_page=results_per_page)
