from typing import Dict, List

from metabolights_utils.models.isa.common import AssayTechnique, IsaTableFile


class AssignmentFile(IsaTableFile):
    identified_metabolite_names: List[str] = []
    metabolite_assignments: Dict[str, str] = {}
    assay_technique: AssayTechnique = AssayTechnique()
    number_of_rows: int = 0
    number_of_assigned_rows: int = 0
    number_of_unassigned_rows: int = 0
