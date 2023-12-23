from typing import Dict, List

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.isa.common import AssayTechnique, IsaTableFile


class AssignmentFile(IsaTableFile):
    identified_metabolite_names: Annotated[List[str], Field(description="")] = []
    metabolite_assignments: Annotated[Dict[str, str], Field(description="")] = {}
    assay_technique: Annotated[AssayTechnique, Field(description="")] = AssayTechnique()
    number_of_rows: Annotated[int, Field(description="")] = 0
    number_of_assigned_rows: Annotated[int, Field(description="")] = 0
    number_of_unassigned_rows: Annotated[int, Field(description="")] = 0
