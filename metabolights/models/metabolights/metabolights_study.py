from typing import Dict, List

from pydantic import Field
from typing_extensions import Annotated

from metabolights.models.common import MetabolightsBaseModel
from metabolights.models.isa.assay_file import AssayFile
from metabolights.models.isa.assignment_file import AssignmentFile
from metabolights.models.isa.investigation_file import Investigation
from metabolights.models.isa.samples_file import SamplesFile
from metabolights.models.parser.common import ParserMessage


class BaseMetabolightsStudyModel(MetabolightsBaseModel):
    version: Annotated[
        str, Field(description="Version of Metabolights Study Model")
    ] = "v1.0"

    investigation_file_path: Annotated[
        str, Field(description="relative path of investigation file")
    ] = ""

    investigation: Annotated[
        Investigation, Field(description="Content of investigation file.")
    ] = Investigation()

    samples: Annotated[
        Dict[str, SamplesFile],
        Field(
            description="Samples files and their contents. "
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
        Field(description="Parser messages for each file."),
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
    ] = []

    tags: Annotated[
        List[str],
        Field(description="Tags for study."),
    ] = []
