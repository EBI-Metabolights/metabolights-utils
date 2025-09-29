from typing import Dict, List

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.isa.assay_file import AssayFile
from metabolights_utils.models.isa.assignment_file import AssignmentFile
from metabolights_utils.models.isa.investigation_file import Investigation
from metabolights_utils.models.isa.samples_file import SamplesFile
from metabolights_utils.models.parser.common import ParserMessage


class BaseMetabolightsStudyModel(MetabolightsBaseModel):
    version: Annotated[
        str, Field(description="Version of Metabolights Study Model")
    ] = "v1.1"

    investigation_file_path: Annotated[
        str,
        Field(
            description="Relative path of investigation file. e.g., i_Investigation.txt"
        ),
    ] = ""

    investigation: Annotated[
        Investigation, Field(description="Content of i_Investigation.txt file.")
    ] = Investigation()

    samples: Annotated[
        Dict[str, SamplesFile],
        Field(
            description="Dictionary of sample files and their content. "
            "Only one sample file can be referenced in investigation file."
        ),
    ] = {}

    assays: Annotated[
        Dict[str, AssayFile],
        Field(
            description="Study assay files and their contents. "
            "Multiple assay files can be defined in investigation file."
        ),
    ] = {}

    parser_messages: Annotated[
        Dict[str, List[ParserMessage]],
        Field(
            description="An dictionary to store parser message list for each ISA metadata file contains any type of parser message."
        ),
    ] = {}

    referenced_assignment_files: Annotated[
        List[str],
        Field(
            description="Relative paths of all assignment files referenced in assay files."
        ),
    ] = []
    referenced_raw_files: Annotated[
        List[str],
        Field(description="Relative paths of all raw files referenced in assay files."),
    ] = []
    referenced_derived_files: Annotated[
        List[str],
        Field(
            description="Relative paths of all derived files referenced in assay files."
        ),
    ] = []
    folders_in_hierarchy: Annotated[
        List[str],
        Field(
            description="Relative folder paths that contain files referenced in assay files."
        ),
    ] = []

    metabolite_assignments: Annotated[
        Dict[str, AssignmentFile],
        Field(description="Metabolite assignment files and their contents."),
    ] = {}

    tags: Annotated[
        List[str],
        Field(description="Tag values for the study."),
    ] = []
