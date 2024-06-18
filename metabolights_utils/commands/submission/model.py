from typing import Dict, List, Union

from metabolights_utils.common import CamelCaseModel


class FtpLoginCredentials(CamelCaseModel):
    user_name: str = ""
    password: str = ""


class RestApiCredentials(CamelCaseModel):
    api_token: str = ""


class LoginCredentials(CamelCaseModel):
    ftp_login: Dict[str, FtpLoginCredentials] = {}
    rest_api_credentials: Dict[str, RestApiCredentials] = {}


class ResponseFileDescriptor(CamelCaseModel):
    created_at: Union[None, str] = None
    directory: bool = False
    file: Union[None, str] = None
    status: Union[None, str] = None
    timestamp: Union[None, str] = None
    type: Union[None, str] = None
    relative_path: Union[None, str] = None
    extension: Union[None, str] = None
    is_stop_folder: bool = False
    is_empty: bool = False


class StudyResponse(CamelCaseModel):
    study: List[ResponseFileDescriptor] = []
    upload_path: Union[None, str] = None
    obfuscation_code: Union[None, str] = None


class SubmittedStudySummary(CamelCaseModel):
    accession: Union[None, str] = None
    created_date: Union[None, str] = None
    release_date: Union[None, str] = None
    curation_request: Union[None, str] = None
    description: Union[None, str] = None
    status: Union[None, str] = None
    title: Union[None, str] = None
    updated: Union[None, str] = None


class SubmittedStudiesResponse(CamelCaseModel):
    data: List[SubmittedStudySummary] = []
