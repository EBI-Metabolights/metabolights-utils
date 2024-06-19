from typing import List

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.isa.common import AssayTechnique, IsaTableFile


class AssayFile(IsaTableFile):
    sample_names: Annotated[
        List[str],
        Field(description="Unique values in `Sample Name` column in the assay file."),
    ] = []

    assay_names: Annotated[
        List[str],
        Field(description="Unique values in `Assay Name` column in the assay file."),
    ] = []

    referenced_assignment_files: Annotated[
        List[str],
        Field(
            description="Relative paths of Metabolite Assignment File in the assay file."
        ),
    ] = []

    referenced_raw_files: Annotated[
        List[str],
        Field(description="Relative paths of referenced raw files in the assay file."),
    ] = []

    referenced_derived_files: Annotated[
        List[str],
        Field(
            description="Relative paths of referenced derived files in the assay file."
        ),
    ] = []

    referenced_raw_file_extensions: Annotated[
        List[str],
        Field(
            description="Unique file extensions of referenced raw files in the assay file."
        ),
    ] = []

    referenced_derived_file_extensions: Annotated[
        List[str],
        Field(
            description="Unique file extensions of referenced derived files in the assay file."
        ),
    ] = []

    assay_technique: Annotated[
        AssayTechnique, Field(description="Assay technique information.")
    ] = AssayTechnique()

    number_of_assay_rows: Annotated[
        int,
        Field(description="Number of assay rows."),
    ] = 0
