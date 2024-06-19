import re
from typing import Dict, List, Set

from pydantic import BaseModel, Field
from typing_extensions import Annotated

ftp_list = r"([\-\w]+)\s+(\d+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+\s+\w+\s+[\w:]+)\s+(.*)\s*"
ftp_list_response_pattern = re.compile(ftp_list)


class FtpResponse(BaseModel):
    success: bool = False
    code: int = -1
    message: str = ""


class FtpFiles(FtpResponse):
    files: List[str] = []


class LocalDirectory(FtpResponse):
    root_path: str = ""
    local_files: List[str] = []
    local_folders: List[str] = []
    actions: Dict[str, str] = {}


class FtpFileDescriptor(BaseModel):
    base_name: Annotated[str, Field(description="")] = ""
    size_in_bytes: Annotated[int, Field(description="")] = 0
    is_directory: Annotated[bool, Field(description="")] = False
    is_link: Annotated[bool, Field(description="")] = False
    mode: Annotated[str, Field(description="")] = ""


class FtpFolderContent(FtpFiles):
    source_directory: str = ""
    folders: List[str] = []
    links: Set[str] = set()
    descriptors: List[FtpFileDescriptor] = []

    def parse_line(self, line: str) -> None:
        if line and line.strip():
            result = ftp_list_response_pattern.search(line)
            if result and result.groups():
                groups = result.groups()
                mode = groups[0][1:]
                binary_mode = re.sub(r"[^0]", "1", mode.replace("-", "0"))
                octal_mode = oct(int(binary_mode, 2)).replace("0o", "")
                filename = groups[6]
                size = groups[4]
                size_in_bytes = 0
                if size.isnumeric():
                    size_in_bytes = int(size)
                descriptor = FtpFileDescriptor(
                    mode=octal_mode, base_name=filename, size_in_bytes=size_in_bytes
                )

                if groups[0].startswith("l"):
                    descriptor.is_link = True
                    self.links.add(filename)
                elif groups[0].startswith("d"):
                    self.folders.append(groups[6])
                    descriptor.is_directory = True
                else:
                    self.files.append(groups[6])
                self.descriptors.append(descriptor)
