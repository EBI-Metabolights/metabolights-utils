import os
import pathlib
import re

from metabolights_utils.models.isa.study_folder_metadata import (
    StudyFileDescriptor,
    StudyFolderMetadata,
)

IGNORED_FILE_PATTERNS = {r"^audit.*$", r"^chebi_pipeline_annotations.*$"}

RAW_FILE_EXTENSIONS = [
    ".d",
    ".raw",
    ".d.zip",
    ".raw.zip",
    ".idb",
    ".cdf",
    ".wiff",
    ".scan",
    ".dat",
    ".cmp",
    ".cdf.cmp",
    ".lcd",
    ".abf",
    ".jpf",
    ".xps",
    ".mgf",
    ".qgd",
    ".hr",
]

RAW_FILE_PATTERNS = {f"^[\w].*({'|'.join(RAW_FILE_EXTENSIONS)})$"}

DERIVED_FILE_EXTENSIONS = {
    ".mzml",
    ".imzml",
    ".wiff",
    ".nmrml",
    ".mzxml",
    ".xml",
    ".mzdata",
    ".cef",
    ".cnx",
    ".peakml",
    ".xy",
    ".smp",
    ".scan",
    ".dx",
    ".msp",
    ".xlsx",
    ".cdf",
    ".mgf",
}

DERIVED_FILE_PATTERNS = {f"^[\w].*({'|'.join(DERIVED_FILE_EXTENSIONS)})$"}

COMPRESSED_FILE_EXTENSIONS = [
    ".zip",
    "zipx",
    ".gz",
    ".tar",
    ".7z",
    ".z",
    ".g7z",
    ".arj",
    ".rar",
    ".bz2",
    ".arj",
    ".z",
    ".war",
]

COMPRESSED_FILE_PATTERNS = {f"^[\w].*({'|'.join(COMPRESSED_FILE_EXTENSIONS)})$"}

TAG_PATTERNS = {
    "type:hidden_file": {r"^\..*$"},
    "type:isatab_file/assay": {r"^a_[\w].*\.txt$"},
    "type:isatab_file/samples": {r"^s_[\w].*\.txt$"},
    "type:isatab_file/investigation": {r"^i_[\w].*\.txt$"},
    "type:isatab_file/assignments": {r"^m_[\w].*\.tsv$"},
    "type:raw_file": RAW_FILE_PATTERNS,
    "type:derived_file": DERIVED_FILE_PATTERNS,
    "type:compressed_file": COMPRESSED_FILE_PATTERNS,
    "type:internal_file": {
        r"^validation_files.json.*$",
        r"^validation_report.json.*$",
        r"^metexplore_mapping.json.*$",
        r"^missing_files.txt.*$",
        r"^files-all.json.*",
    },
}


class FolderMetadataCollector(object):
    def __init__(self):
        pass

    def get_folder_metadata(self, study_path):
        study_path = pathlib.Path(study_path)

        result = study_path.rglob("*")
        study_folder_metadata = StudyFolderMetadata()
        total_folder_size_in_bytes = 0
        for item in result:
            relative_path = str(item).replace(
                f"{str(study_path).rstrip(os.sep)}{os.sep}", ""
            )
            in_ignore_list = False
            for pattern in IGNORED_FILE_PATTERNS:
                if re.match(pattern, relative_path):
                    in_ignore_list = True
                    break
            if in_ignore_list:
                continue

            parent_directory = os.path.dirname(relative_path)
            base_name = os.path.basename(relative_path)
            descriptor = StudyFileDescriptor()

            for tag in TAG_PATTERNS:
                for pattern in TAG_PATTERNS[tag]:
                    if re.match(pattern, base_name, re.IGNORECASE):
                        descriptor.tags.append(tag)

            descriptor.extension = item.suffix
            descriptor.baseName = base_name
            descriptor.parentDirectory = parent_directory
            descriptor.filePath = relative_path
            descriptor.isDirectory = not item.is_file()
            descriptor.isLink = item.is_symlink()
            stats = os.stat(item)
            if descriptor.isDirectory:
                descriptor.sizeInBytes = 0
            else:
                descriptor.sizeInBytes = stats.st_size
            descriptor.createdAt = int(stats.st_ctime)
            descriptor.modifiedAt = int(stats.st_mtime)
            descriptor.mode = oct(stats.st_mode & 0o777).replace("0o", "")

            if item.is_file():
                study_folder_metadata.files[relative_path] = descriptor
            else:
                study_folder_metadata.folders[relative_path] = descriptor
            total_folder_size_in_bytes += descriptor.sizeInBytes
        study_folder_metadata.folderSizeInBytes = total_folder_size_in_bytes

        self.get_size_in_string(study_folder_metadata, total_folder_size_in_bytes)
        return study_folder_metadata

    def get_size_in_string(self, study_folder_metadata, total_folder_size_in_bytes):
        if total_folder_size_in_bytes / (1024**3) >= 1:
            study_folder_metadata.folderSizeInStr = (
                str(round(total_folder_size_in_bytes / (1024**3), 2)) + "GB"
            )
        else:
            study_folder_metadata.folderSizeInStr = (
                str(round(total_folder_size_in_bytes / (1024**2), 2)) + "MB"
            )
