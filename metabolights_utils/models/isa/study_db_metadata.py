from typing import Dict, List, Optional

from metabolights_utils.models.isa.common import IsaAbstractModel
from metabolights_utils.models.isa.enums import StudyStatus, UserRole, UserStatus


class Submitter(IsaAbstractModel):
    dbId: int = -1
    orcid: str = ""
    address: str = ""
    joinDate: str = ""
    userName: str = ""
    firstName: str = ""
    lastName: str = ""
    affiliation: str = ""
    affiliationUrl: str = ""
    status: UserStatus = UserStatus.FROZEN
    role: UserRole = UserRole.ANONYMOUS

    class Config:
        orm_mode = True


class StudyDBMetadata(IsaAbstractModel):
    dbId: int = -1
    studyId: str = ""
    numericStudyId: int = -1
    obfuscationCode: str = ""
    studySize: Optional[int] = -1
    submissionDate: str = ""
    releaseDate: str = ""
    updateDate: str = ""
    statusDate: str = ""
    studyTypes: List[str] = []
    status: StudyStatus = StudyStatus.DORMANT
    overrides: Dict[str, str] = {}
    submitters: List[Submitter] = []
