import sys
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from functools import reduce
from typing import Any, Dict, List, Tuple, Union

from pydantic import BaseModel

from metabolights_utils.models.isa.common import (
    SortType,
    SortValueClassification,
    TsvFileSortOption,
)


def get_sort_value_order(
    sort_option: TsvFileSortOption, classification: SortValueClassification
):
    if sort_option.value_order & 0o007 == classification:
        return 3
    elif (sort_option.value_order & 0o070) >> 3 == classification:
        return 2
    return 1


def sort_by_multiple_column(sequence, sort_order):
    return reduce(
        lambda s, order: sorted(s, key=order[0], reverse=order[1]),
        reversed(sort_order),
        sequence,
    )


def get_sorter(sort_option: TsvFileSortOption, col_index: int):
    def row_sorter(filtered_row: Tuple[int, List[str]]):
        val = filtered_row[1][col_index]
        sorter = SORTERS[sort_option.column_sort_type]
        return sorter.sort(sort_option, val)

    return row_sorter


# SORTERS


class AbstractSorter(ABC):
    @abstractmethod
    def sort(
        self, sort_option: TsvFileSortOption, value: str
    ) -> Union[int, float, str, datetime]:
        pass


class IntegerSorter(AbstractSorter):
    def get_int_value_by_order(self, order: int, valid_value_order: int):
        if order == 1:
            return -sys.maxsize - 1
        elif order == 2:
            if valid_value_order > order:
                return -sys.maxsize
            else:
                return sys.maxsize - 1
        return sys.maxsize

    def sort(self, sort_option: TsvFileSortOption, value: str) -> int:
        if not value:
            order = get_sort_value_order(sort_option, SortValueClassification.EMPTY)
            valid_value_order = get_sort_value_order(
                sort_option, SortValueClassification.VALID
            )
            return self.get_int_value_by_order(order, valid_value_order)

        try:
            return int(value)
        except Exception as exc:
            order = get_sort_value_order(sort_option, SortValueClassification.INVALID)
            valid_value_order = get_sort_value_order(
                sort_option, SortValueClassification.VALID
            )
            return self.get_int_value_by_order(order, valid_value_order)


class FloatSorter(AbstractSorter):
    def get_float_value_by_order(self, order: int, valid_value_order: int):
        if order == 1:
            return sys.float_info.min
        elif order == 2:
            if valid_value_order > order:
                return sys.float_info.min + 1
            else:
                return sys.float_info.max - 1
        return sys.float_info.max

    def sort(self, sort_option: TsvFileSortOption, value: str) -> float:
        if not value:
            order = get_sort_value_order(sort_option, SortValueClassification.EMPTY)
            valid_value_order = get_sort_value_order(
                sort_option, SortValueClassification.VALID
            )
            return self.get_float_value_by_order(order, valid_value_order)

        try:
            return float(value)
        except Exception as exc:
            order = get_sort_value_order(sort_option, SortValueClassification.INVALID)
            valid_value_order = get_sort_value_order(
                sort_option, SortValueClassification.VALID
            )
            return self.get_float_value_by_order(order, valid_value_order)


class DateTimeSorter(AbstractSorter):
    DATETIME_MIN_MINUS_1 = datetime.min.replace(
        microsecond=(datetime.min.microsecond + 1)
    )
    DATETIME_MAX_MINUS_1 = datetime.max.replace(
        microsecond=(datetime.max.microsecond - 1)
    )

    def get_datetime_value_by_order(self, order: int, valid_value_order: int):
        if order == 1:
            return datetime.min
        elif order == 2:
            if valid_value_order > order:
                return DateTimeSorter.DATETIME_MIN_MINUS_1
            else:
                return DateTimeSorter.DATETIME_MAX_MINUS_1
        return datetime.max

    def sort(self, sort_option: TsvFileSortOption, value: str) -> datetime:
        if not value:
            order = get_sort_value_order(sort_option, SortValueClassification.EMPTY)
            valid_value_order = get_sort_value_order(
                sort_option, SortValueClassification.VALID
            )
            return self.get_datetime_value_by_order(order, valid_value_order)

        try:
            return datetime.strptime(value, sort_option.default_datetime_pattern)
        except Exception as exc:
            order = get_sort_value_order(sort_option, SortValueClassification.INVALID)
            valid_value_order = get_sort_value_order(
                sort_option, SortValueClassification.VALID
            )
            return self.get_datetime_value_by_order(order, valid_value_order)


class StringSorter(AbstractSorter):
    def sort(self, sort_option: TsvFileSortOption, value: str) -> str:
        if not value:
            return "~"
        if sort_option.case_sensitive:
            return f"~{value}"
        return f"~{value.lower()}"


SORTERS: Dict[SortType, AbstractSorter] = {}
SORTERS[SortType.INTEGER] = IntegerSorter()
SORTERS[SortType.STRING] = StringSorter()
SORTERS[SortType.FLOAT] = FloatSorter()
SORTERS[SortType.DATETIME] = DateTimeSorter()
