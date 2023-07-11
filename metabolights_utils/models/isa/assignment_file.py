from typing import Dict, List

from metabolights_utils.models.isa.common import AssayTechnique, IsaTableFile


class AssignmentFile(IsaTableFile):
    identifiedMetaboliteNames: List[str] = []
    metaboliteAssignments: Dict[str, str] = {}
    assayTechnique: AssayTechnique = AssayTechnique()
    numberOfRows: int = 0
    numberOfAssignedRows: int = 0
    numberOfUnassignedRows: int = 0
