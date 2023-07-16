from typing import Dict, List

from pydantic import Field

from metabolights_utils.models.isa.assay_file import AssayFile
from metabolights_utils.models.isa.assignment_file import AssignmentFile
from metabolights_utils.models.isa.investigation_file import Investigation
from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.parser.common import ParserMessage
from metabolights_utils.models.isa.samples_file import SamplesFile


class BaseMetabolightsStudyModel(MetabolightsBaseModel):
    version: str = "v1.0"
    investigationFilePath: str = ""
    investigation: Investigation = Field(Investigation())
    samples: Dict[str, SamplesFile] = Field({})
    assays: Dict[str, AssayFile] = Field({})

    parserMessages: Dict[str, List[ParserMessage]] = Field({})

    referencedAssignmentFiles: List[str] = []
    referencedRawFiles: List[str] = []
    referencedDerivedFiles: List[str] = []
    foldersInHierarchy: List[str] = []

    metaboliteAssignments: Dict[str, AssignmentFile] = Field({})
    tags: List[str] = []
