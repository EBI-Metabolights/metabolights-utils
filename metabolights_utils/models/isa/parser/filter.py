import re
from datetime import datetime
from enum import Enum
from functools import partial
from typing import Any, Dict, Union

from pydantic import BaseModel

from metabolights_utils.models.isa.common import (
    FilterOperation,
    FilterParameterType,
    TsvFileFilterOption,
)


def get_filter_operation(filter_option: TsvFileFilterOption):
    def filter(filter_option: TsvFileFilterOption, row_value: str):
        filter_method = FILTER_METHODS[filter_option.operation]
        if filter_option.negate_result:
            return not filter_method(filter_option, row_value)
        else:
            return filter_method(filter_option, row_value)

    return partial(filter, filter_option)


# FILTERS
def filter_contains(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    if filter_option.case_sensitive:
        if row_value and str(filter_option.parameter) in row_value:
            return True
    else:
        if row_value and str(filter_option.parameter).lower() in row_value.lower():
            return True
    return False


def filter_startswith(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    if filter_option.case_sensitive:
        if row_value and str(row_value).startswith(str(filter_option.parameter)):
            return True
    else:
        if row_value and str(row_value).lower().startswith(
            str(filter_option.parameter).lower()
        ):
            return True
    return False


def filter_endswith(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    if filter_option.case_sensitive:
        if row_value and str(row_value).endswith(str(filter_option.parameter)):
            return True
    else:
        if row_value and str(row_value).lower().endswith(
            str(filter_option.parameter).lower()
        ):
            return True
    return False


def filter_equal(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    if filter_option.case_sensitive:
        if row_value and str(row_value) == str(filter_option.parameter):
            return True
    else:
        if row_value and str(row_value).lower() == str(filter_option.parameter).lower():
            return True
    return False


def filter_greater(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    if row_value:
        try:
            if filter_option.parameter_type == FilterParameterType.AUTO:
                if isinstance(filter_option.parameter, int):
                    return (
                        True if int(row_value) > int(filter_option.parameter) else False
                    )
                elif isinstance(filter_option.parameter, float):
                    return (
                        True
                        if float(row_value) > float(filter_option.parameter)
                        else False
                    )
                else:
                    return (
                        True if str(row_value) > str(filter_option.parameter) else False
                    )
            elif filter_option.parameter_type == FilterParameterType.INTEGER:
                return True if int(row_value) > int(filter_option.parameter) else False
            elif filter_option.parameter_type == FilterParameterType.FLOAT:
                return (
                    True if float(row_value) > float(filter_option.parameter) else False
                )
            elif filter_option.parameter_type == FilterParameterType.DATETIME:
                return (
                    True
                    if datetime.strptime(
                        row_value, filter_option.default_datetime_pattern
                    )
                    > datetime.strptime(
                        filter_option.parameter, filter_option.default_datetime_pattern
                    )
                    else False
                )
            else:
                return True if str(row_value) > str(filter_option.parameter) else False
        except:
            return False
    return False


def filter_greater_equal(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    if row_value:
        try:
            if filter_option.parameter_type == FilterParameterType.AUTO:
                if isinstance(filter_option.parameter, int):
                    return (
                        True
                        if int(row_value) >= int(filter_option.parameter)
                        else False
                    )
                elif isinstance(filter_option.parameter, float):
                    return (
                        True
                        if float(row_value) >= float(filter_option.parameter)
                        else False
                    )
                else:
                    return (
                        True
                        if str(row_value) >= str(filter_option.parameter)
                        else False
                    )
            elif filter_option.parameter_type == FilterParameterType.INTEGER:
                return True if int(row_value) >= int(filter_option.parameter) else False
            elif filter_option.parameter_type == FilterParameterType.FLOAT:
                return (
                    True
                    if float(row_value) >= float(filter_option.parameter)
                    else False
                )
            elif filter_option.parameter_type == FilterParameterType.DATETIME:
                return (
                    True
                    if datetime.strptime(
                        row_value, filter_option.default_datetime_pattern
                    )
                    >= datetime.strptime(
                        filter_option.parameter, filter_option.default_datetime_pattern
                    )
                    else False
                )
            else:
                return True if str(row_value) >= str(filter_option.parameter) else False
        except:
            return False
    return False


def filter_less(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    param, param_type = filter_option.parameter, filter_option.parameter_type
    if row_value and param:
        try:
            if param_type == FilterParameterType.AUTO:
                if isinstance(param, int):
                    return True if int(row_value) < int(param) else False
                elif isinstance(param, float):
                    return True if float(row_value) < float(param) else False
                else:
                    return True if str(row_value) < str(param) else False
            elif param_type == FilterParameterType.INTEGER:
                return True if int(row_value) < int(param) else False
            elif param_type == FilterParameterType.FLOAT:
                return True if float(row_value) < float(param) else False
            elif param_type == FilterParameterType.DATETIME:
                return (
                    True
                    if datetime.strptime(
                        row_value, filter_option.default_datetime_pattern
                    )
                    < datetime.strptime(param, filter_option.default_datetime_pattern)
                    else False
                )
            else:
                return True if str(row_value) < str(param) else False
        except:
            return False
    return False


def filter_less_equal(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    param, param_type = filter_option.parameter, filter_option.parameter_type
    if row_value and param:
        try:
            if param_type == FilterParameterType.AUTO:
                if isinstance(param, int):
                    return True if int(row_value) <= int(param) else False
                elif isinstance(param, float):
                    return True if float(row_value) <= float(param) else False
                else:
                    return True if str(row_value) <= str(param) else False
            elif param_type == FilterParameterType.INTEGER:
                return True if int(row_value) <= int(param) else False
            elif param_type == FilterParameterType.FLOAT:
                return True if float(row_value) <= float(param) else False
            elif param_type == FilterParameterType.DATETIME:
                return (
                    True
                    if datetime.strptime(
                        row_value, filter_option.default_datetime_pattern
                    )
                    <= datetime.strptime(param, filter_option.default_datetime_pattern)
                    else False
                )
            else:
                return True if str(row_value) <= str(param) else False
        except:
            return False
    return False


def filter_empty(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    return True if not row_value else False


def filter_regex(filter_option: TsvFileFilterOption, row_value: str) -> bool:
    if row_value and filter_option.parameter:
        try:
            if filter_option.case_sensitive:
                result = re.match(filter_option.parameter, row_value)
            else:
                result = re.match(filter_option.parameter, row_value, re.IGNORECASE)
            return True if result else False
        except:
            return False
    return False


FILTER_METHODS: Dict[FilterOperation, Any] = {}
FILTER_METHODS[FilterOperation.CONTAINS] = filter_contains
FILTER_METHODS[FilterOperation.STARTSWITH] = filter_startswith
FILTER_METHODS[FilterOperation.ENDSWITH] = filter_endswith
FILTER_METHODS[FilterOperation.EQUAL] = filter_equal
FILTER_METHODS[FilterOperation.GREATER] = filter_greater
FILTER_METHODS[FilterOperation.GREATER_EQUAL] = filter_greater_equal
FILTER_METHODS[FilterOperation.LESS] = filter_less
FILTER_METHODS[FilterOperation.LESS_EQUAL] = filter_less_equal
FILTER_METHODS[FilterOperation.EMPTY] = filter_empty
FILTER_METHODS[FilterOperation.REGEX] = filter_regex
