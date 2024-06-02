from enum import Enum
from typing import Dict, List, Optional

from pydantic import ConfigDict

from metabolights_utils.common import CamelCaseModel
from metabolights_utils.models.common import GenericMessage
from metabolights_utils.models.isa.common import IsaAbstractModel
from metabolights_utils.models.metabolights.metabolights_study import (
    BaseMetabolightsStudyModel,
)


class UserStatus(str, Enum):
    NEW = "NEW"
    VERIFIED = "VERIFIED"
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"

    @staticmethod
    def get_from_int(int_value: int):
        if int_value == 0:
            return UserStatus.NEW
        elif int_value == 1:
            return UserStatus.VERIFIED
        elif int_value == 2:
            return UserStatus.ACTIVE
        else:
            return UserStatus.FROZEN


class UserRole(str, Enum):
    SUBMITTER = "SUBMITTER"
    CURATOR = "CURATOR"
    ANONYMOUS = "ANONYMOUS"

    @staticmethod
    def get_from_int(int_value: int):
        if int_value == 0:
            return UserRole.SUBMITTER
        elif int_value == 1:
            return UserRole.CURATOR
        else:
            return UserRole.ANONYMOUS


class CurationRequest(int, Enum):
    MANUAL_CURATION = 0
    NO_CURATION = 1
    SEMI_AUTOMATED_CURATION = 2


class StudyStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    INCURATION = "INCURATION"
    INREVIEW = "INREVIEW"
    PUBLIC = "PUBLIC"
    DORMANT = "DORMANT"

    @staticmethod
    def get_from_int(int_value: int):
        if int_value == 0:
            return StudyStatus.SUBMITTED
        elif int_value == 1:
            return StudyStatus.INCURATION
        elif int_value == 2:
            return StudyStatus.INREVIEW
        elif int_value == 3:
            return StudyStatus.PUBLIC
        else:
            return StudyStatus.DORMANT


class StudyFileDescriptor(IsaAbstractModel):
    file_path: str = ""
    base_name: str = ""
    parent_directory: str = ""
    extension: str = ""
    size_in_bytes: int = 0
    is_directory: bool = False
    is_link: bool = False
    modified_at: int = 0
    created_at: int = 0
    mode: str = ""
    tags: List[str] = []


class StudyFolderMetadata(IsaAbstractModel):
    folder_size_in_bytes: int = -1
    folder_size_in_str: str = ""
    folders: Dict[str, StudyFileDescriptor] = {}
    files: Dict[str, StudyFileDescriptor] = {}


class Submitter(CamelCaseModel):
    db_id: int = -1
    orcid: str = ""
    address: str = ""
    join_date: str = ""
    user_name: str = ""
    first_name: str = ""
    last_name: str = ""
    affiliation: str = ""
    affiliation_url: str = ""
    status: UserStatus = UserStatus.FROZEN
    role: UserRole = UserRole.ANONYMOUS

    model_config = ConfigDict(from_attributes=True)


class StudyDBMetadata(CamelCaseModel):
    db_id: int = -1
    study_id: str = ""
    numeric_study_id: int = -1
    obfuscation_code: str = ""
    study_size: Optional[int] = -1
    submission_date: str = ""
    release_date: str = ""
    update_date: str = ""
    status_date: str = ""
    study_types: List[str] = []
    status: StudyStatus = StudyStatus.DORMANT
    curation_request: CurationRequest = CurationRequest.MANUAL_CURATION
    overrides: Dict[str, str] = {}
    submitters: List[Submitter] = []


class MetabolightsStudyModel(BaseMetabolightsStudyModel):
    study_db_metadata: StudyDBMetadata = StudyDBMetadata()
    study_folder_metadata: StudyFolderMetadata = StudyFolderMetadata()

    folder_reader_messages: List[GenericMessage] = []
    db_reader_messages: List[GenericMessage] = []
    has_db_metadata: bool = False
    has_sample_table_data: bool = False
    has_assay_table_data: bool = False
    has_assignment_table_data: bool = False
    has_folder_metadata: bool = False
    has_investigation_data: bool = False
