from enum import Enum


class GenericMessageType(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ParserMessageType(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ColumnsStructure(str, Enum):
    SINGLE_COLUMN = "SINGLE_COLUMN"
    ONTOLOGY_COLUMN = "ONTOLOGY_COLUMN"
    SINGLE_COLUMN_AND_UNIT_ONTOLOGY = "SINGLE_COLUMN_AND_UNIT_ONTOLOGY"
    LINKED_COLUMN = "LINKED_COLUMN"
    ADDITIONAL_COLUMN = "ADDITIONAL_COLUMN"
    INVALID_MULTI_COLUMN = "UNKNOWN"


class IsaTableAdditionalColumn(str, Enum):
    UNIT = "Unit"
    TERM_SOURCE_REF = "Term Source REF"
    TERM_ACCSSION_NUMBER = "Term Accession Number"


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
