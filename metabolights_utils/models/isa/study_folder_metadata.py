from typing import Dict, List

from metabolights_utils.models.isa.common import IsaAbstractModel


class StudyFileDescriptor(IsaAbstractModel):
    filePath: str = ""
    baseName: str = ""
    parentDirectory: str = ""
    extension: str = ""
    sizeInBytes: int = 0
    isDirectory: bool = False
    isLink: bool = False
    modifiedAt: int = 0
    createdAt: int = 0
    mode: str = ""
    tags: List[str] = []


class StudyFolderMetadata(IsaAbstractModel):
    folderSizeInBytes: int = -1
    folderSizeInStr: str = ""
    folders: Dict[str, StudyFileDescriptor] = {}
    files: Dict[str, StudyFileDescriptor] = {}
