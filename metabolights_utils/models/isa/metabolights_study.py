from typing import Dict, List

from pydantic import BaseModel, Field

from metabolights_utils.models.isa.assay_file import AssayFile
from metabolights_utils.models.isa.assignment_file import AssignmentFile
from metabolights_utils.models.isa.investigation_file import Investigation
from metabolights_utils.models.isa.messages import GenericMessage, ParserMessage
from metabolights_utils.models.isa.samples_file import SamplesFile
from metabolights_utils.models.isa.study_db_metadata import StudyDBMetadata
from metabolights_utils.models.isa.study_folder_metadata import StudyFolderMetadata


class MetabolightsStudyModel(BaseModel):
    version: str = "v1.0"
    investigationFilePath: str = ""
    investigation: Investigation = Field(Investigation())
    samples: Dict[str, SamplesFile] = Field({})
    assays: Dict[str, AssayFile] = Field({})
    studyDBMetadata: StudyDBMetadata = StudyDBMetadata()

    parserMessages: Dict[str, List[ParserMessage]] = Field({})
    folderReaderMessages: List[GenericMessage] = Field([])
    dbReaderMessages: List[GenericMessage] = Field([])

    referencedAssignmentFiles: List[str] = []
    referencedRawFiles: List[str] = []
    referencedDerivedFiles: List[str] = []
    foldersInHierarchy: List[str] = []

    metaboliteAssignments: Dict[str, AssignmentFile] = Field({})
    studyFolderMetadata = StudyFolderMetadata()
    tags: List[str] = []
