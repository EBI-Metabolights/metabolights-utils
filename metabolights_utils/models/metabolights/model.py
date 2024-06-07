from enum import Enum
from typing import Dict, List, Union

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

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
    file_path: Annotated[str, Field(description="")] = ""
    base_name: Annotated[str, Field(description="")] = ""
    parent_directory: Annotated[str, Field(description="")] = ""
    extension: Annotated[str, Field(description="")] = ""
    size_in_bytes: Annotated[int, Field(description="")] = 0
    is_directory: Annotated[bool, Field(description="")] = False
    is_link: Annotated[bool, Field(description="")] = False
    modified_at: Annotated[int, Field(description="")] = 0
    created_at: Annotated[int, Field(description="")] = 0
    mode: Annotated[str, Field(description="")] = ""
    tags: Annotated[List[str], Field(description="")] = []


class StudyFolderMetadata(IsaAbstractModel):
    folder_size_in_bytes: Annotated[int, Field(description="")] = -1
    folder_size_in_str: Annotated[str, Field(description="")] = ""
    folders: Annotated[Dict[str, StudyFileDescriptor], Field(description="")] = {}
    files: Annotated[Dict[str, StudyFileDescriptor], Field(description="")] = {}


class Submitter(CamelCaseModel):
    db_id: Annotated[int, Field(description="")] = -1
    orcid: Annotated[str, Field(description="")] = ""
    address: Annotated[str, Field(description="")] = ""
    join_date: Annotated[str, Field(description="")] = ""
    user_name: Annotated[str, Field(description="")] = ""
    first_name: Annotated[str, Field(description="")] = ""
    last_name: Annotated[str, Field(description="")] = ""
    affiliation: Annotated[str, Field(description="")] = ""
    affiliation_url: Annotated[str, Field(description="")] = ""
    status: Annotated[UserStatus, Field(description="")] = UserStatus.FROZEN
    role: Annotated[UserRole, Field(description="")] = UserRole.ANONYMOUS

    model_config = ConfigDict(from_attributes=True)


class StudyDBMetadata(CamelCaseModel):
    db_id: Annotated[int, Field(description="")] = -1
    study_id: Annotated[str, Field(description="")] = ""
    numeric_study_id: Annotated[int, Field(description="")] = -1
    obfuscation_code: Annotated[str, Field(description="")] = ""
    study_size: Annotated[Union[None, int], Field(description="")] = -1
    submission_date: Annotated[str, Field(description="")] = ""
    release_date: Annotated[str, Field(description="")] = ""
    update_date: Annotated[str, Field(description="")] = ""
    status_date: Annotated[str, Field(description="")] = ""
    study_types: Annotated[List[str], Field(description="")] = []
    status: Annotated[StudyStatus, Field(description="")] = StudyStatus.DORMANT
    curation_request: Annotated[CurationRequest, Field(description="")] = (
        CurationRequest.MANUAL_CURATION
    )
    overrides: Annotated[Dict[str, str], Field(description="")] = {}
    submitters: Annotated[List[Submitter], Field(description="")] = []


class MetabolightsStudyModel(BaseMetabolightsStudyModel):
    study_db_metadata: Annotated[StudyDBMetadata, Field(description="")] = (
        StudyDBMetadata()
    )
    study_folder_metadata: Annotated[StudyFolderMetadata, Field(description="")] = (
        StudyFolderMetadata()
    )

    folder_reader_messages: Annotated[
        List[GenericMessage], Field(description="Folder ")
    ] = []
    db_reader_messages: Annotated[
        List[GenericMessage], Field(description="DB reader messages.")
    ] = []
    has_db_metadata: Annotated[
        bool, Field(description="True if database metadata is loaded.")
    ] = False
    has_sample_table_data: Annotated[
        bool, Field(description="True if sample file is loaded.")
    ] = False
    has_assay_table_data: Annotated[
        bool, Field(description="True if assay files are loaded.")
    ] = False
    has_assignment_table_data: Annotated[
        bool, Field(description="True if assignment files are loaded")
    ] = False
    has_folder_metadata: Annotated[
        bool, Field(description="True if folder metadata is complete.")
    ] = False
    has_investigation_data: Annotated[
        bool, Field(description="True if investtigation file is loaded.")
    ] = False
