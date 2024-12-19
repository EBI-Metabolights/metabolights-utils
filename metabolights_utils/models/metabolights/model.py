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


class CurationRequest(str, Enum):
    MANUAL_CURATION = "MANUAL_CURATION"
    NO_CURATION = "NO_CURATION"
    SEMI_AUTOMATED_CURATION = "SEMI_AUTOMATED_CURATION"

    @staticmethod
    def get_from_int(int_value: int):
        if int_value == 0:
            return CurationRequest.MANUAL_CURATION
        elif int_value == 1:
            return CurationRequest.NO_CURATION
        elif int_value == 2:
            return CurationRequest.SEMI_AUTOMATED_CURATION
        return CurationRequest.MANUAL_CURATION


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
    file_path: Annotated[
        str, Field(description="File relative path. e.g., FILES/RAW_FILES/raw_data.d")
    ] = ""
    base_name: Annotated[
        str,
        Field(
            description="File basename. e.g., raw_data.d for FILES/RAW_FILES/raw_data.d"
        ),
    ] = ""
    parent_directory: Annotated[
        str,
        Field(
            description="Relative parent directory. e.g., FILES/RAW_FILES for FILES/RAW_FILES/raw_data.d"
        ),
    ] = ""
    extension: Annotated[
        str,
        Field(
            description="File extension. e.g., .d for raw_data.d for FILES/RAW_FILES/raw_data.d"
        ),
    ] = ""
    size_in_bytes: Annotated[int, Field(description="Size of file in bytes.")] = 0
    is_directory: Annotated[
        bool, Field(description="True if the file is a folder.")
    ] = False
    is_link: Annotated[
        bool, Field(description="True if the file is a symbolic link.")
    ] = False
    modified_at: Annotated[
        int,
        Field(
            description="Modified time of the file. The value is a timestamp in UTC."
        ),
    ] = 0
    created_at: Annotated[
        int,
        Field(
            description="Creation time of the file. The value is a timestamp in UTC."
        ),
    ] = 0
    mode: Annotated[
        str, Field(description="File permission mode in octal. e.g., 775")
    ] = ""
    tags: Annotated[List[str], Field(description="Tag values for the file.")] = []


class StudyFolderMetadata(IsaAbstractModel):
    data_folder_size_calculated: Annotated[
        bool, Field(description="True if data folder size is calculated.")
    ] = False
    metadata_folder_size_calculated: Annotated[
        bool, Field(description="True if metadata folder size is calculated.")
    ] = False
    folder_size_in_bytes: Annotated[
        int,
        Field(
            description="Study folder size in bytes. Folder size may be size of metadata files,"
            + " data files or both depends on data_folder_size_calculated or metadata_folder_size_calculated."
        ),
    ] = -1
    folder_size_in_str: Annotated[
        str, Field(description="Human readable study folder size in MB or GB")
    ] = ""
    folders: Annotated[
        Dict[str, StudyFileDescriptor],
        Field(
            description="Folders and summary information about each one within a study folder."
        ),
    ] = {}
    files: Annotated[
        Dict[str, StudyFileDescriptor],
        Field(
            description="Files and summary information about each one within a study folder."
        ),
    ] = {}


class Submitter(CamelCaseModel):
    db_id: Annotated[int, Field(description="Database unique id for submitter.")] = -1
    orcid: Annotated[str, Field(description="ORCID of submitter.")] = ""
    address: Annotated[str, Field(description="Address of submitter.")] = ""
    join_date: Annotated[str, Field(description="Registration date of submitter.")] = ""
    user_name: Annotated[
        str, Field(description="username (email address) of submitter.")
    ] = ""
    first_name: Annotated[str, Field(description="First name of submitter.")] = ""
    last_name: Annotated[str, Field(description="Last name of submitter.")] = ""
    affiliation: Annotated[str, Field(description="Submitter's affiliation.")] = ""
    affiliation_url: Annotated[
        str, Field(description="Submitter's affiliation webpage URL.")
    ] = ""
    status: Annotated[UserStatus, Field(description="Status of user.")] = (
        UserStatus.FROZEN
    )
    role: Annotated[UserRole, Field(description="Role of submmiter.")] = (
        UserRole.ANONYMOUS
    )

    model_config = ConfigDict(from_attributes=True)


class StudyDBMetadata(CamelCaseModel):
    db_id: Annotated[int, Field(description="Database unique id for study.")] = -1
    study_id: Annotated[str, Field(description="Study accession number.")] = ""
    numeric_study_id: Annotated[
        int,
        Field(
            description="Numarical part of study accession number. e.g., 123 for MTBLS123"
        ),
    ] = -1
    obfuscation_code: Annotated[
        str, Field(description="Obfusication code of study.")
    ] = ""
    study_size: Annotated[
        Union[None, int], Field(description="Total size (bytes) of study folder.")
    ] = -1
    submission_date: Annotated[str, Field(description="Study submission date.")] = ""
    release_date: Annotated[
        str, Field(description="Study public release date (actual or anticipated.)")
    ] = ""
    update_date: Annotated[str, Field(description="Last update date of study.")] = ""
    status_date: Annotated[
        str, Field(description="Last status update date of study.")
    ] = ""
    study_types: Annotated[
        List[str], Field(description="Study types defined by curators.")
    ] = []
    status: Annotated[StudyStatus, Field(description="Status of study.")] = (
        StudyStatus.DORMANT
    )
    curation_request: Annotated[
        CurationRequest,
        Field(
            description="Curation request. e.g., no curation request, manual curation request."
        ),
    ] = CurationRequest.MANUAL_CURATION
    overrides: Annotated[
        Dict[str, str], Field(description="Overrided validation rules.")
    ] = {}
    submitters: Annotated[
        List[Submitter], Field(description="Submitters of study.")
    ] = []


class MetabolightsStudyModel(BaseMetabolightsStudyModel):
    study_db_metadata: Annotated[
        StudyDBMetadata,
        Field(
            description="Basic metatada information (status, database id, etc.) stored in database."
        ),
    ] = StudyDBMetadata()

    study_folder_metadata: Annotated[
        StudyFolderMetadata,
        Field(description="Descriptors of files and folders within study folder."),
    ] = StudyFolderMetadata()

    folder_reader_messages: Annotated[
        List[GenericMessage], Field(description="Folder reader messages.")
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
