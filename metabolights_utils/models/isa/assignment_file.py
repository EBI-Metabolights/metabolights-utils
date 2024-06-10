from typing import Dict, List

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.isa.common import AssayTechnique, IsaTableFile


class AssignmentFile(IsaTableFile):
    identified_metabolite_names: Annotated[
        List[str], Field(description="Names of metabolites defined in the ISA table.")
    ] = []
    metabolite_assignments: Annotated[
        Dict[str, str],
        Field(
            description="Metabolite names and assigned CHEBI id values in the ISA table."
        ),
    ] = {}
    assay_technique: Annotated[
        AssayTechnique,
        Field(
            description="Assay technique of assays that reference the current m_*.tsv file."
        ),
    ] = AssayTechnique()
    number_of_rows: Annotated[
        int, Field(description="Number of rows in ISA table.")
    ] = 0
    number_of_assigned_rows: Annotated[
        int, Field(description="Number of rows assigned a CHEBI id.")
    ] = 0
    number_of_unassigned_rows: Annotated[
        int, Field(description="Number of rows not assigned a CHEBI id.")
    ] = 0
