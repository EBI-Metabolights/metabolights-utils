from typing import Dict, List

from pydantic import Field

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.isa.assay_file import AssayFile
from metabolights_utils.models.isa.assignment_file import AssignmentFile
from metabolights_utils.models.isa.investigation_file import Investigation
from metabolights_utils.models.isa.samples_file import SamplesFile
from metabolights_utils.models.parser.common import ParserMessage


class BaseMetabolightsStudyModel(MetabolightsBaseModel):
    version: str = "v1.0"
    investigation_file_path: str = ""
    investigation: Investigation = Field(Investigation())
    samples: Dict[str, SamplesFile] = Field({})
    assays: Dict[str, AssayFile] = Field({})

    parser_messages: Dict[str, List[ParserMessage]] = Field({})

    referenced_assignment_files: List[str] = []
    referenced_raw_files: List[str] = []
    referenced_derived_files: List[str] = []
    folders_in_hierarchy: List[str] = []

    metabolite_assignments: Dict[str, AssignmentFile] = Field({})
    tags: List[str] = []
