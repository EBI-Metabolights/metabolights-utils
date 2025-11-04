import datetime
import glob
import logging
import os
import re
import subprocess
from typing import Dict, List, Tuple, Union

from metabolights_utils.models.common import GenericMessage, InfoMessage, WarningMessage
from metabolights_utils.models.metabolights.model import (
    StudyFileDescriptor,
    StudyFolderMetadata,
)
from metabolights_utils.provider import definitions
from metabolights_utils.provider.study_provider import AbstractFolderMetadataCollector
from metabolights_utils.provider.utils import is_metadata_filename_pattern

logger = logging.getLogger(__name__)


class LocalFolderMetadataCollector(AbstractFolderMetadataCollector):
    def __init__(self):
        pass

    def visit_folder(
        self,
        directory: str,
        root_path: str,
        metadata: Dict[str, StudyFileDescriptor],
        messages: List[GenericMessage],
        metadata_files_only: bool = False,
        data_files_mapping_folder_name: None | str = None,
    ):
        try:
            dir_relative_path = str(directory).replace(
                f"{str(root_path).rstrip(os.sep)}", ""
            )
            dir_relative_path = dir_relative_path.lstrip("/")
            skip_content = False
            for pattern in definitions.skip_folder_content_patterns:
                if pattern.match(dir_relative_path):
                    skip_content = True
                    break
            if skip_content:
                messages.append(
                    InfoMessage(
                        short=f"{dir_relative_path} directory is in content ignore list. SKIPPED"
                    )
                )
                return
            if data_files_mapping_folder_name and directory == root_path:
                # emulate folder
                parent = os.path.dirname(data_files_mapping_folder_name)
                parent = parent if not parent.startswith(".") else ""
                base = os.path.basename(data_files_mapping_folder_name)
                descriptor = StudyFileDescriptor(
                    base_name=base,
                    file_path=data_files_mapping_folder_name,
                    parent_directory=parent,
                    is_directory=True,
                    is_link=False,
                    created_at=int(datetime.datetime.now().timestamp()),
                    mode="755",
                )
                metadata[data_files_mapping_folder_name] = descriptor

            entries = os.listdir(directory)
            for entry in entries:
                full_path: str = os.path.join(directory, entry)

                if metadata_files_only:
                    if not is_metadata_filename_pattern(entry):
                        continue
                    if not os.path.isfile(full_path):
                        continue

                relative_path = os.path.join(dir_relative_path, entry)
                base_name = os.path.basename(relative_path)
                parent_directory = os.path.dirname(relative_path)
                in_ignore_list = False
                for pattern in definitions.ignore_file_patterns:
                    if pattern.match(relative_path):
                        in_ignore_list = True
                        break
                if in_ignore_list:
                    messages.append(
                        InfoMessage(
                            short=f"{relative_path} is in ignore list. SKIPPED."
                        )
                    )
                    continue

                descriptor = StudyFileDescriptor()

                for tag in definitions.TAG_PATTERNS:
                    for pattern in definitions.TAG_PATTERNS[tag]:
                        if re.match(pattern, base_name, re.IGNORECASE):
                            descriptor.tags.append(tag)
                _, ext = os.path.splitext(relative_path)
                key = relative_path
                key_parent = parent_directory
                if data_files_mapping_folder_name:
                    key = os.path.join(data_files_mapping_folder_name, relative_path)
                    key_parent = os.path.join(
                        data_files_mapping_folder_name, relative_path
                    )
                descriptor.extension = ext
                descriptor.base_name = base_name
                descriptor.parent_directory = key_parent
                descriptor.file_path = key
                descriptor.is_directory = os.path.isdir(full_path)
                descriptor.is_link = os.path.islink(full_path)
                if os.path.exists(full_path):
                    stats = os.stat(full_path)
                    if descriptor.is_directory:
                        descriptor.size_in_bytes = 0
                    else:
                        descriptor.size_in_bytes = stats.st_size
                    descriptor.created_at = int(stats.st_ctime)
                    descriptor.modified_at = int(stats.st_mtime)
                    descriptor.mode = oct(stats.st_mode & 0o777).replace("0o", "")
                metadata[key] = descriptor

                if os.path.isdir(full_path):
                    self.visit_folder(
                        full_path,
                        root_path,
                        metadata=metadata,
                        messages=messages,
                        metadata_files_only=metadata_files_only,
                        data_files_mapping_folder_name=data_files_mapping_folder_name,
                    )

        except PermissionError as ex:
            messages.append(
                WarningMessage(
                    short=f"{directory} directory permission error {str(ex)}"
                )
            )
        except Exception as exc:
            messages.append(
                WarningMessage(short=f"{directory} directory error {str(exc)}")
            )

    def get_folder_metadata(
        self,
        study_path,
        calculate_data_folder_size: bool = False,
        calculate_metadata_size: bool = False,
        data_files_path: str = "FILES",
        data_files_mapping_folder_name: None | str = None,
    ) -> Tuple[Union[None, StudyFolderMetadata], List[GenericMessage]]:
        messages: List[GenericMessage] = []
        study_folder_metadata = StudyFolderMetadata()
        metadata: Dict[str, StudyFileDescriptor] = {}
        self.visit_folder(
            study_path,
            study_path,
            metadata=metadata,
            messages=messages,
            metadata_files_only=True,
            data_files_mapping_folder_name=None,
        )
        search_path = data_files_path
        if not os.path.isabs(data_files_path) and not data_files_path.startswith(
            study_path
        ):
            merged_path = os.path.join(study_path, data_files_path)
            if os.path.exists(merged_path):
                search_path = merged_path

        self.visit_folder(
            search_path,
            search_path,
            metadata=metadata,
            messages=messages,
            metadata_files_only=False,
            data_files_mapping_folder_name=data_files_mapping_folder_name,
        )
        study_folder_metadata.folders = {
            x: metadata[x] for x in metadata if metadata[x].is_directory
        }
        study_folder_metadata.files = {
            x: metadata[x] for x in metadata if not metadata[x].is_directory
        }
        data_folder_size = 0
        if calculate_data_folder_size:
            files_folder_path = os.path.join(study_path, "FILES")
            if os.path.exists(files_folder_path):
                size = self.folder_size(files_folder_path)
                data_folder_size = size if size else 0

            study_folder_metadata.folder_size_in_bytes = data_folder_size

        if calculate_metadata_size:
            metadata_size = 0
            metadata_files = glob.glob(f"{study_path}/[asi]_*.txt")
            metadata_files = [x for x in metadata_files]
            maf_files = glob.glob(f"{study_path}/m_*.tsv")
            metadata_files.extend([x for x in maf_files])

            for item in metadata_files:
                stats = os.stat(item)
                metadata_size += stats.st_size

            if study_folder_metadata.folder_size_in_bytes >= 0:
                study_folder_metadata.folder_size_in_bytes += metadata_size
            else:
                study_folder_metadata.folder_size_in_bytes = metadata_size

        total_size = study_folder_metadata.folder_size_in_bytes
        if total_size > -1:
            if total_size / (1024**3) >= 1:
                study_folder_metadata.folder_size_in_str = (
                    str(round(total_size / (1024**3), 2)) + "GB"
                )
            else:
                study_folder_metadata.folder_size_in_str = (
                    str(round(total_size / (1024**2), 2)) + "MB"
                )

        return study_folder_metadata, messages

    def folder_size(self, directory: str) -> Union[int, None]:
        try:
            # Run the 'du' command to get the size of the directory in bytes
            directory = os.path.realpath(directory)
            result = subprocess.run(
                ["du", "-s", directory],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                size_str = result.stdout.split()[0]
                return int(size_str) * 1000
            else:
                logger.error("Error", result.stderr.strip())
                return None
        except FileNotFoundError as e:
            logger.exception(e)
            return None
        except Exception as e:
            logger.exception(e)
            return None


if __name__ == "__main__":
    local = LocalFolderMetadataCollector()
    metadata_path = "/Users/ozgury/work/development/mztabm2mtbls/submission_validation_test/studies/MTBLS263"
    data_files_path = "/Users/ozgury/work/development/mztabm2mtbls/submission_validation_test/studies/MTBLS263/FILES"
    result, messages = local.get_folder_metadata(
        metadata_path,
        data_files_path=data_files_path,
        data_files_mapping_folder_name="FILES",
    )
    pass
