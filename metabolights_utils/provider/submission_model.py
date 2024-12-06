import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, TypeVar, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from metabolights_utils.common import CamelCaseModel


class ValidationMessage(BaseModel):
    message: str = ""
    section: str = ""
    val_sequence: str = ""
    status: str = ""
    metadata_file: str = ""
    value: str = ""
    description: str = ""
    val_override: str = ""
    val_message: str = ""
    comment: str = ""


class Section(BaseModel):
    section: str = ""
    has_more_items: bool = False
    details: List[ValidationMessage] = []


class Validation(BaseModel):
    version: str = ""
    status: str = ""
    timig: Union[float, int] = 0.0
    last_update_time: str = ""
    last_update_timestamp: Union[float, int] = 0
    validations: List[Section] = []


class ValidationReport(BaseModel):
    validation: Validation = Validation()


class ValidationTaskStatus(BaseModel):
    task_id: str = ""
    last_update_time: float = 0
    last_update_timestamp: str = ""
    last_status: str = ""
    task_done_time: float = 0
    task_done_time_str: str = ""


class ValidationResponse(BaseModel):
    new_task: bool = False
    message: str = ""
    task: ValidationTaskStatus = ValidationTaskStatus()


class ValidationResponseV2(CamelCaseModel):
    status: bool = False
    status_message: str = ""
    task: ValidationTaskStatus = ValidationTaskStatus()


T = TypeVar("T", bound=CamelCaseModel)

LIST_ITEM = TypeVar("LIST_ITEM")


class Status(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class APIValidationError(CamelCaseModel):
    type: Annotated[
        str,
        Field(description="Validation error type"),
    ] = ""

    loc: Annotated[
        Union[str, List[Union[int, str]]],
        Field(description="Location of the error"),
    ] = ""
    msg: Annotated[
        str,
        Field(description="Error message"),
    ] = ""

    input: Annotated[
        Union[str, Dict[str, Any]],
        Field(description="Input data that caused the error"),
    ] = ""


class APIBaseResponse(CamelCaseModel):
    status: Annotated[
        Status,
        Field(description="Status of the response. It can be `success` or `error`"),
    ] = Status.SUCCESS

    success_message: Annotated[
        Union[None, str],
        Field(
            description="If status is `success`, response may contain success message."
            "It may contain a message for partial success even if response status is `error`."
        ),
    ] = None

    error_message: Annotated[
        Union[None, str],
        Field(description="If status is `error`, response may contain error message."),
    ] = None

    errors: Annotated[
        Union[List[str], List[APIValidationError]],
        Field(
            description="If status is `error`, response may contain a list of error details."
        ),
    ] = []


class APIResponse(APIBaseResponse, Generic[T]):
    """
    API response model for non-paginated results.
    """

    content: Annotated[
        Union[None, T],
        Field(description="If status is `success`, this stores response data."),
    ] = None


class WorkerTaskStatus(BaseModel):
    task_id: Annotated[
        str,
        Field(
            description="This field contains task id of the task.",
        ),
    ] = ""
    task_status: Annotated[
        str,
        Field(
            description="This field contains status of the task. Values: INITIATED, STARTED, SUCCESS, FAILURE, REVOKED, PENDING, etc.",
        ),
    ] = ""
    message: Annotated[
        str,
        Field(
            description="Message related to the task",
        ),
    ] = ""


class PolicyMessageType(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    SUCCESS = "SUCCESS"


class PolicyMessage(CamelCaseModel):
    identifier: str = ""
    title: str = ""
    description: str = ""
    section: str = ""
    priority: str = ""
    type: PolicyMessageType = PolicyMessageType.INFO
    violation: str = ""
    source_file: str = ""
    source_column_header: str = ""
    source_column_index: Union[str, int] = ""
    has_more_miolations: bool = False
    total_violations: int = 0
    values: List[str] = []
    technique: str = ""


class OpaValidationResult(BaseModel):
    violations: Annotated[List[PolicyMessage], Field()] = []
    summary: Annotated[List[PolicyMessage], Field([])] = []


class PolicySummaryResult(BaseModel):
    study_id: str = ""
    start_time: Union[None, str, datetime.datetime] = None
    completion_time: Union[None, str, datetime.datetime] = None
    duration_in_seconds: float = 0
    messages: OpaValidationResult = OpaValidationResult()
    metadata_updates: List[str] = []
    metadata_modifier_enabled: bool = False
    assay_file_techniques: Dict[str, str] = {}
    maf_file_techniques: Dict[str, str] = {}


class PolicyResultResponse(WorkerTaskStatus):
    task_result: Annotated[
        PolicySummaryResult,
        Field(
            description="This field contains task id of the task.",
        ),
    ] = PolicySummaryResult()


class FtpUploadDetails(BaseModel):
    study_id: str
    ftp_folder: str
    ftp_host: str
    ftp_user: str
    ftp_password: str
