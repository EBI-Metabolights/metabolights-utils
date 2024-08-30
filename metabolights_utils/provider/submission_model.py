from typing import List, Union

from pydantic import BaseModel


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
