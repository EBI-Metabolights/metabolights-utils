import re
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, EnumMeta
from typing import Any, Dict, List, Set, Union

from pydantic import Field

from metabolights_utils.common import CamelCaseModel
from metabolights_utils.tsv.sort import TsvSortException


class TsvFilterException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class FilterDataType(str, Enum):
    AUTO = "AUTO"
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    DATETIME = "DATETIME"


class FilterOperation(str, Enum):
    CONTAINS = "like"
    EQUAL = "eq"
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"
    GREATER = "gt"
    GREATER_EQUAL = "ge"
    LESS = "lt"
    LESS_EQUAL = "le"
    REGEX = "regex"
    EMPTY = "empty"
    CUSTOM = "custom"


class TsvFileFilterOption(CamelCaseModel):
    search_columns: List[str] = Field(
        [],
        description="Search column names. Search in any column if it is None or empty",
    )
    search_ignore_columns: List[str] = Field(
        [],
        description="Ignore selected columns if search column is None or empty",
    )
    operation: FilterOperation = Field(
        FilterOperation.CONTAINS, description="Filter operation"
    )
    parameter: Union[str, int, float, datetime] = Field(
        "", description="Parameter for the filter operation"
    )
    data_type: FilterDataType = Field(
        FilterDataType.AUTO, description="Apply filter with the given data type"
    )
    case_sensitive: bool = Field(
        True, description="String operations will be applied in case sensitive mode"
    )
    negate_result: bool = Field(
        False, description="Reverse result after apply operation"
    )
    default_datetime_pattern: str = Field(
        "%d/%m/%Y", description="Convert string value to datetime using this pattern"
    )
    custom_filter_arguments: Dict[str, Any] = Field(
        {}, description="Additional arguments for custom filters"
    )
    custom_filter_name: str = Field({}, description="Registered custom filter name")


class Filter(ABC):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        self.column_name_indices = column_name_indices
        self.column_indices = column_indices
        self.filter_option: TsvFileFilterOption = filter_option

        if not filter_option:
            raise TsvFilterException("Filter option is not valid")

        if self.filter_option.search_columns:
            invalid_columns = []
            for column in self.filter_option.search_columns:
                if not column in self.column_name_indices:
                    invalid_columns.append(column)
            if invalid_columns:
                raise TsvFileFilterOption(
                    f"Invalid search columns: {', '.join(invalid_columns)}"
                )
        else:
            self.filter_option.search_columns = []

        if self.filter_option.search_ignore_columns:
            invalid_columns = []
            for column in self.filter_option.search_ignore_columns:
                if not column in self.column_name_indices:
                    invalid_columns.append(column)
            if invalid_columns:
                raise TsvFileFilterOption(
                    f"Invalid search ignore columns: {', '.join(invalid_columns)}"
                )
        else:
            self.filter_option.search_ignore_columns = []

        self.target_column_indices: Set[int] = set(
            self.column_name_indices[column_name]
            for column_name in self.column_name_indices
            if column_name in self.filter_option.search_columns
        )
        if not self.filter_option.search_columns:
            all_indices: Set[int] = set(self.column_indices.keys())
            ignore_column_indices: Set[int] = set(
                self.column_name_indices[column_name]
                for column_name in self.column_name_indices
                if column_name in self.filter_option.search_ignore_columns
            )
            self.target_column_indices = all_indices.difference(ignore_column_indices)

        self.parameter: Union[int, str, float, datetime] = (
            filter_option.parameter if filter_option.parameter is not None else ""
        )
        if not filter_option.case_sensitive and isinstance(self.parameter, str):
            self.parameter = filter_option.parameter.lower()

        self.parameter_data_type = self.filter_option.data_type

        if filter_option.operation != FilterOperation.CUSTOM:
            if self.filter_option.data_type == FilterDataType.AUTO:
                if isinstance(self.filter_option.parameter, float):
                    self.parameter_data_type = FilterDataType.FLOAT
                elif isinstance(self.filter_option.parameter, int):
                    self.parameter_data_type = FilterDataType.INTEGER
                elif isinstance(self.filter_option.parameter, datetime):
                    self.parameter_data_type = FilterDataType.DATETIME
                else:
                    self.parameter_data_type = FilterDataType.STRING
                self.parameter = self.convert_to_selected_data_type(self.parameter)

    def convert_to_selected_data_type(self, value):
        if self.parameter_data_type == FilterDataType.FLOAT:
            return float(value)
        elif self.parameter_data_type == FilterDataType.INTEGER:
            return int(value)
        elif self.parameter_data_type == FilterDataType.DATETIME:
            pattern = self.filter_option.default_datetime_pattern
            return datetime.strptime(value, pattern)
        if not value:
            return ""

        return value if self.filter_option.case_sensitive else value.lower()

    def get_updated_value(self, value: str):
        if value is None:
            return ""
        return value if self.filter_option.case_sensitive else value.lower()

    def filter(self, row: List[str]) -> bool:
        match = False
        for index in self.target_column_indices:
            if self.evaluate(row[index]):
                match = True
                break

        return not match if self.filter_option.negate_result else match

    @abstractmethod
    def evaluate(self, row_value: str):
        pass


class CustomFilter(Filter, ABC):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)


class FilterRegistry:
    custom_filters: Dict[str, Any] = {}
    default_filters: Dict[str, Any] = {}

    @classmethod
    def register_filter(cls, name: str, filter: Any) -> None:
        cls.default_filters[name] = filter

    @classmethod
    def get_filter(
        cls,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> Filter:
        name = ""
        if filter_option.operation == FilterOperation.CUSTOM:
            name = filter_option.custom_filter_name
            if name in cls.custom_filters:
                return cls.custom_filters[name](
                    filter_option, column_name_indices, column_indices
                )
        else:
            name = filter_option.operation.value
            if name in cls.default_filters:
                return cls.default_filters[name](
                    filter_option, column_name_indices, column_indices
                )
        raise TsvFilterException(f"Filter name {name} is not registered")

    @classmethod
    def register_custom_filter(cls, name: str, filter: Any) -> None:
        cls.custom_filters[name] = filter

    @classmethod
    def unregister_custom_filter(cls, name: str) -> None:
        if name in cls.custom_filters:
            del cls.custom_filters[name]

    @classmethod
    def get_custom_filter(
        cls,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> Filter:
        name = filter_option.custom_filter_name
        if name and name in cls.custom_filters:
            return cls.custom_filters[name](
                filter_option, column_name_indices, column_indices
            )
        return None


# FILTERS


class CustomFilterProxy(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)
        self.custom_filter: CustomFilter = FilterRegistry.get_custom_filter(
            self.filter_option
        )

    def evaluate(self, row_value: str) -> bool:
        if not self.custom_filter:
            return False
        return self.custom_filter.evaluate(row_value)


class ContainsFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        value = self.get_updated_value(row_value)
        return True if self.parameter in value else False


class StartsWithFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        value = self.get_updated_value(row_value)
        return True if value.startswith(self.parameter) else False


class EndsWithFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        value = self.get_updated_value(row_value)
        return True if value.endswith(self.parameter) else False


class EqualFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        value = self.get_updated_value(row_value)
        return True if value == self.parameter else False


class GreaterFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        if row_value:
            try:
                value = self.convert_to_selected_data_type(row_value)
                return True if value > self.parameter else False
            except:
                return False
        return False


class GreaterEqualFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        if row_value:
            try:
                value = self.convert_to_selected_data_type(row_value)
                return True if value >= self.parameter else False
            except:
                return False
        return False


class LessFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        if row_value:
            try:
                value = self.convert_to_selected_data_type(row_value)
                return True if value < self.parameter else False
            except:
                return False
        return False


class LessEqualFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        if row_value:
            try:
                value = self.convert_to_selected_data_type(row_value)
                return True if value <= self.parameter else False
            except:
                return False
        return False


class EmptyFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        return True if not row_value else False


class RegexFilter(Filter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        value = self.get_updated_value(row_value)
        return True if re.match(self.parameter, value) else False


FilterRegistry.register_filter(FilterOperation.CONTAINS.value, ContainsFilter)
FilterRegistry.register_filter(FilterOperation.STARTSWITH.value, StartsWithFilter)
FilterRegistry.register_filter(FilterOperation.ENDSWITH.value, EndsWithFilter)
FilterRegistry.register_filter(FilterOperation.EQUAL.value, EqualFilter)
FilterRegistry.register_filter(FilterOperation.GREATER.value, GreaterFilter)
FilterRegistry.register_filter(FilterOperation.GREATER_EQUAL.value, GreaterEqualFilter)
FilterRegistry.register_filter(FilterOperation.LESS.value, LessFilter)
FilterRegistry.register_filter(FilterOperation.LESS_EQUAL.value, LessEqualFilter)
FilterRegistry.register_filter(FilterOperation.EMPTY.value, EmptyFilter)
FilterRegistry.register_filter(FilterOperation.REGEX.value, RegexFilter)
FilterRegistry.register_filter(FilterOperation.CUSTOM.value, CustomFilterProxy)


class ValidNumberCustomFilter(CustomFilter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        try:
            _ = float(row_value)
            return True
        except:
            return False


class ValidDatetimeCustomFilter(CustomFilter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

    def evaluate(self, row_value: str) -> bool:
        try:
            value = datetime.strptime(
                row_value, self.filter_option.default_datetime_pattern
            )
            return True if value else False
        except:
            return False


class EnumContainsCustomFilter(CustomFilter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)

        if "enum-class" in filter_option.custom_filter_arguments:
            self.enum_class = filter_option.custom_filter_arguments["enum-class"]
            try:
                if isinstance(self.enum_class, str):
                    splitted_value = self.enum_class.split(":")

                    if len(splitted_value) == 2:
                        self.enum_class = getattr(
                            sys.modules[splitted_value[0]], splitted_value[1]
                        )
                    else:
                        raise TsvFilterException(
                            f"Selected enum class name is not valid. Use format <module name>:<enum class name>"
                        )
            except Exception as exc:
                if isinstance(exc, TsvFilterException):
                    raise exc
                raise TsvFilterException(
                    f"selected class name is not converted to enum: {str(exc)}"
                )
        if not isinstance(self.enum_class, EnumMeta):
            raise TsvFilterException("selected class is not enum")

        self.enum_string_map: Dict[str, str] = {}
        if "enum-value-map" in filter_option.custom_filter_arguments:
            self.enum_value_map = filter_option.custom_filter_arguments[
                "enum-value-map"
            ]
            if not isinstance(self.enum_value_map, dict) or not self.enum_value_map:
                raise TsvFilterException("Enum map is not valid dict")

            for key in self.enum_value_map:
                value = self.enum_value_map[key]
                if self.filter_option.case_sensitive:
                    self.enum_string_map[str(key)] = str(value)
                else:
                    self.enum_string_map[str(key)] = str(value).lower()

            enum_values = {str(e.value) for e in self.enum_class}
            missing_values = [x for x in enum_values if x not in self.enum_string_map]
            if missing_values:
                raise TsvSortException(
                    f"There are some missing values to map an enum {', '.join(missing_values)}"
                )

    def evaluate(self, row_value: str) -> bool:
        try:
            value = self.parameter in self.enum_string_map[row_value]
            return True if value else False
        except Exception:
            return False


class BetweenEqualCustomFilter(CustomFilter):
    def __init__(
        self,
        filter_option: TsvFileFilterOption,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(filter_option, column_name_indices, column_indices)
        self.min = None
        self.max = None
        if "min" in self.filter_option.custom_filter_arguments:
            self.min = self.filter_option.custom_filter_arguments["min"]
        if "max" in self.filter_option.custom_filter_arguments:
            self.max = self.filter_option.custom_filter_arguments["max"]
        self.min = self.convert_to_selected_data_type(self.min)
        self.max = self.convert_to_selected_data_type(self.max)

    def evaluate(self, row_value: str) -> bool:
        if row_value:
            try:
                value = self.convert_to_selected_data_type(row_value)
                return True if self.min <= value <= self.max else False
            except:
                return False
        return False


FilterRegistry.register_custom_filter("between-equal", BetweenEqualCustomFilter)
FilterRegistry.register_custom_filter("valid-datetime", ValidDatetimeCustomFilter)
FilterRegistry.register_custom_filter("valid-number", ValidNumberCustomFilter)
FilterRegistry.register_custom_filter("enum-contains", EnumContainsCustomFilter)
