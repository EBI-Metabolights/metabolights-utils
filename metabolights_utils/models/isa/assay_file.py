from typing import List

from metabolights_utils.models.isa.common import AssayTechnique, IsaTableFile


class AssayFile(IsaTableFile):
    sample_names: List[str] = []
    assay_names: List[str] = []
    referenced_assignment_files: List[str] = []
    referenced_raw_files: List[str] = []
    referenced_derived_files: List[str] = []

    referenced_raw_file_extensions: List[str] = []
    referenced_derived_file_extensions: List[str] = []
    assay_technique: AssayTechnique = AssayTechnique()
    number_of_assay_rows: int = 0
