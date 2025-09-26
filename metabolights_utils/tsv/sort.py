import sys
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, EnumMeta
from typing import Any, Callable, Dict, List, Tuple

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.common import CamelCaseModel


class SortType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATETIME = "datetime"
    CUSTOM = "custom"


class SortValueClassification(int, Enum):
    EMPTY = 1
    INVALID = 2
    VALID = 3


class TsvFileSortValueOrder(int, Enum):
    EMPTY_INVALID_VALID = 0o123
    EMPTY_VALID_INVALID = 0o132
    INVALID_EMPTY_VALID = 0o213
    INVALID_VALID_EMPTY = 0o231
    VALID_INVALID_EMPTY = 0o321
    VALID_EMPTY_INVALID = 0o312


class TsvFileSortOption(CamelCaseModel):
    column_name: Annotated[
        str,
        Field(
            description="Column name that sort operation will be applied."
            " Column name may be different "
            "if there are multiple columns with same name."
            "If there are multiple column headers, "
            "Second column and others are named as "
            "<column header>.1 <column header>.2 and so on.",
        ),
    ] = ""

    reverse: Annotated[bool, Field(description="Sort descending order")] = False

    column_sort_type: Annotated[
        SortType, Field(description="Sort value with the given type")
    ] = SortType.STRING

    case_sensitive: Annotated[
        bool, Field(description="Sort string values in case sensitive order")
    ] = True

    default_datetime_pattern: Annotated[
        str, Field(description="Convert string value to datetime using this pattern")
    ] = "%d/%m/%Y"

    value_order: Annotated[
        TsvFileSortValueOrder,
        Field(
            description="Position of valid and empty values "
            "if sort type is int, float or datetime",
        ),
    ] = TsvFileSortValueOrder.VALID_EMPTY_INVALID

    custom_sorter_name: Annotated[
        str, Field(description="Registered custom sorter name")
    ] = ""

    custom_sorter_arguments: Annotated[
        Dict[str, Any], Field(description="Additional arguments for custom sorters")
    ] = {}

    min_key_length: Annotated[
        int,
        Field(
            description="If sort type is not string, "
            "values will be converted to string and "
            "short strings will be filled with 0.",
        ),
    ] = -1


class TsvSortException(Exception):
    def __init__(self, message: str = "") -> None:
        super().__init__(message)


class Sorter(ABC):
    def __init__(
        self,
        sort_option: TsvFileSortOption,
        column_idx: int,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        self.sort_option = sort_option
        self.column_idx = column_idx
        self.column_name_indices = column_name_indices
        self.column_indices = column_indices

        if not sort_option or not sort_option.column_name:
            raise TsvSortException("Invalid sort option")

        if self.column_idx not in self.column_indices:
            raise TsvSortException("Invalid sort index")

        if sort_option.column_name not in self.column_name_indices:
            raise TsvSortException("Column name is not in table columns")

    @abstractmethod
    def sort(self, row: Tuple[int, List[str]]) -> str:
        pass


class SorterRegistry:
    custom_sorters: Dict[str, Callable] = {}
    default_sorters: Dict[str, Callable] = {}

    @classmethod
    def register_sorter(cls, name: str, sorter: Callable) -> None:
        cls.default_sorters[name] = sorter

    @classmethod
    def get_sorter(
        cls,
        sort_option: TsvFileSortOption,
        column_idx: int,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> Sorter:
        name = ""
        if sort_option.column_sort_type == SortType.CUSTOM:
            name = sort_option.custom_sorter_name
            if name in cls.custom_sorters:
                return cls.custom_sorters[name](
                    sort_option, column_idx, column_name_indices, column_indices
                )
        else:
            name = sort_option.column_sort_type.value
            if name in cls.default_sorters:
                return cls.default_sorters[name](
                    sort_option, column_idx, column_name_indices, column_indices
                )
        raise TsvSortException(f"Sorter name {name} is not registered")

    @classmethod
    def register_custom_sorter(cls, name: str, sorter: Any) -> None:
        cls.custom_sorters[name] = sorter

    @classmethod
    def unregister_custom_sorter(cls, name: str) -> None:
        if name in cls.custom_sorters:
            del cls.custom_sorters[name]


# SORTERS


class AbstractSorter(Sorter, ABC):
    NONE_VALUE = "".rjust(20, "0")

    def __init__(
        self,
        sort_option: TsvFileSortOption,
        column_idx: int,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
        default_min_key_length: int = 20,
    ) -> None:
        super().__init__(sort_option, column_idx, column_name_indices, column_indices)
        self.min_key_length = sort_option.min_key_length
        if self.min_key_length < 0:
            self.min_key_length = default_min_key_length

        self.invalid_value_order = self.get_sort_value_order(
            SortValueClassification.INVALID
        )
        self.none_value_order = self.get_sort_value_order(SortValueClassification.EMPTY)
        self.valid_value_order = self.get_sort_value_order(
            SortValueClassification.VALID
        )

    def get_invalid_value(self, value: str):
        length = self.min_key_length
        if self.sort_option.case_sensitive:
            return str(self.invalid_value_order) + str(value).zfill(length)
        else:
            return str(self.invalid_value_order) + str(value.lower()).zfill(length)

    def get_none_value(self):
        return str(self.none_value_order) + self.NONE_VALUE

    def get_sort_value_order(self, classification: SortValueClassification):
        if self.sort_option.value_order & 0o007 == classification:
            return 1 if self.sort_option.reverse else 3
        elif (self.sort_option.value_order & 0o070) >> 3 == classification:
            return 2
        return 3 if self.sort_option.reverse else 1

    def sort(self, row: Tuple[int, List[str]]) -> str:
        value = row[1][self.column_idx]
        if not value:
            return self.get_none_value()
        try:
            order = self.valid_value_order
            length = self.min_key_length
            if length > 0:
                return str(order) + self.get_sorted_string(value).zfill(length)
            else:
                return str(order) + self.get_sorted_string(value)
        except Exception:
            return self.get_invalid_value(value)

    @abstractmethod
    def get_sorted_string(self, value: str) -> str:
        pass


class CustomSorter(AbstractSorter, ABC):
    def __init__(
        self,
        sort_option: TsvFileSortOption,
        column_idx: int,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
        default_min_key_length: int = 0,
    ) -> None:
        super().__init__(
            sort_option,
            column_idx,
            column_name_indices,
            column_indices,
            default_min_key_length=default_min_key_length,
        )


class IntegerSorter(AbstractSorter):
    def __init__(
        self,
        sort_option: TsvFileSortOption,
        column_idx: int,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(sort_option, column_idx, column_name_indices, column_indices)

    def get_sorted_string(self, value: str) -> str:
        return str(int(value))


class FloatSorter(AbstractSorter):
    def __init__(
        self,
        sort_option: TsvFileSortOption,
        column_idx: int,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(sort_option, column_idx, column_name_indices, column_indices)

    def get_sorted_string(self, value: str) -> float:
        return str(int(float(value) * 100000))


class DateTimeSorter(AbstractSorter):
    def __init__(
        self,
        sort_option: TsvFileSortOption,
        column_idx: int,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(sort_option, column_idx, column_name_indices, column_indices)

    def get_sorted_string(self, value: str) -> datetime:
        val = datetime.strptime(value, self.sort_option.default_datetime_pattern)  # noqa: DTZ007
        return str(int(val.timestamp()))


class StringSorter(AbstractSorter):
    def __init__(
        self,
        sort_option: TsvFileSortOption,
        column_idx: int,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(
            sort_option,
            column_idx,
            column_name_indices,
            column_indices,
            default_min_key_length=0,
        )

    def get_sorted_string(self, value: str) -> str:
        if self.sort_option.case_sensitive:
            return f"~{value}"
        return f"~{value.lower()}"


SorterRegistry.register_sorter(SortType.INTEGER.value, IntegerSorter)
SorterRegistry.register_sorter(SortType.STRING.value, StringSorter)
SorterRegistry.register_sorter(SortType.FLOAT.value, FloatSorter)
SorterRegistry.register_sorter(SortType.DATETIME.value, DateTimeSorter)
# SorterRegistry.register_sorter(SortType.CUSTOM.value, CustomSorterProxy)


class EnumSorter(CustomSorter):
    def __init__(
        self,
        sort_option: TsvFileSortOption,
        column_idx: int,
        column_name_indices: Dict[str, int],
        column_indices: Dict[int, str],
    ) -> None:
        super().__init__(
            sort_option,
            column_idx,
            column_name_indices,
            column_indices,
            default_min_key_length=20,
        )

        if "enum-class" in sort_option.custom_sorter_arguments:
            self.enum_class = sort_option.custom_sorter_arguments["enum-class"]
            try:
                if isinstance(self.enum_class, str):
                    splitted_value = self.enum_class.split(":")

                    if len(splitted_value) == 2:
                        self.enum_class = getattr(
                            sys.modules[splitted_value[0]], splitted_value[1]
                        )
                    else:
                        raise TsvSortException(
                            "Selected enum class name is not valid. "
                            "Use format <module name>:<enum class name>"
                        )
            except Exception as exc:
                if isinstance(exc, TsvSortException):
                    raise exc
                raise TsvSortException(
                    "Selected class name is not converted to enum"
                ) from exc
        if not isinstance(self.enum_class, EnumMeta):
            raise TsvSortException("selected class is not enum")

        self.enum_string_map: Dict[str, str] = {}
        if "enum-value-map" in sort_option.custom_sorter_arguments:
            self.enum_value_map = sort_option.custom_sorter_arguments["enum-value-map"]
            if not isinstance(self.enum_value_map, dict) or not self.enum_value_map:
                raise TsvSortException("Enum map is not valid dict")

            for key in self.enum_value_map:
                value = self.enum_value_map[key]
                self.enum_string_map[str(key)] = str(value).zfill(self.min_key_length)

            enum_values = {str(e.value) for e in self.enum_class}
            missing_values = [x for x in enum_values if x not in self.enum_string_map]
            if missing_values:
                raise TsvSortException(
                    "There are some missing values to map an enum "
                    f"{', '.join(missing_values)}"
                )

    def get_sorted_string(self, value: str) -> str:
        return self.enum_string_map[value]


SorterRegistry.register_custom_sorter("enum-sorter", EnumSorter)
