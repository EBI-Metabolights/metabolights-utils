import datetime
import json
import logging
import os
import re
from typing import Dict, List, Tuple, Union

from pydantic import BaseModel

from metabolights_utils.models.common import GenericMessage
from metabolights_utils.models.enums import GenericMessageType
from metabolights_utils.models.metabolights.model import (
    StudyFileDescriptor,
    StudyFolderMetadata,
)
from metabolights_utils.provider import definitions
from metabolights_utils.provider.ftp.default_ftp_client import DefaultFtpClient
from metabolights_utils.provider.study_provider import AbstractFolderMetadataCollector
from metabolights_utils.utils.filename_utils import join_path

logger = logging.getLogger(__name__)


class FolderIndex(BaseModel):
    update_time: Union[None, datetime.datetime, str] = None
    content: Union[None, StudyFolderMetadata] = None


MANAGED_FOLDERS = {"", "FILES", "FILES/RAW_FILES", "FILES/DERIVED_FILES"}


class FtpFolderMetadataCollector(AbstractFolderMetadataCollector):
    def __init__(
        self,
        client: DefaultFtpClient,
        study_id: str,
        folder_index_file_path: str,
        rebuild_folder_index_file: bool = False,
    ):
        if not client or not client.remote_repository_root_directory or not study_id:
            logger.error("Not valid input.")
            raise Exception("Not valid input.")
        self.client = client
        self.study_id = study_id.upper().strip("/")

        self.folder_index_file_path = (
            join_path(folder_index_file_path)
            if folder_index_file_path
            else join_path(
                definitions.default_local_repority_cache_path,
                study_id,
                "mtbls_index.json",
            )
        )
        logger.debug("Folder index path is %s", self.folder_index_file_path)
        self.rebuild_folder_index_file = rebuild_folder_index_file
        self.remote_study_directory = join_path(
            self.client.remote_repository_root_directory, self.study_id
        )
        self.remote_study_directory = self.remote_study_directory.replace(
            "\\", "/"
        ).rstrip("/")

    def visit_folder(
        self,
        directory: str,
        study_path: str,
        metadata: Dict[str, StudyFileDescriptor],
        messages: List[str],
    ):
        try:
            prefix = f"{str(study_path).rstrip('/')}/"
            directory = directory.replace("\\", "/")
            dir_relative_path = (
                str(directory).replace(prefix, "") if study_path != directory else ""
            )

            skip_content = False
            for pattern in definitions.skip_folder_content_patterns:
                if pattern.match(dir_relative_path):
                    skip_content = True
                    break
            if skip_content:
                logger.debug("%s is in ignore list. SKIPPED.", dir_relative_path)
                messages.append(f"{dir_relative_path} is in ignore list. SKIPPED.")
                return
            directory_input = (
                join_path(self.study_id, dir_relative_path)
                if dir_relative_path
                else self.study_id
            )
            result = self.client.list_directory(directory=directory_input)

            required_raw_data_folder_files = [
                x
                for x in result.descriptors
                if not x.is_directory
                and len(x.base_name) > 3
                and x.base_name[:4] == "acqu"
                and "_" not in x.base_name
                and "." not in x.base_name
            ]
            optional_raw_data_folder_files = [
                x
                for x in result.descriptors
                if (
                    (len(x.base_name) > 2 and x.base_name[:3] in ("fid", "ser"))
                    or x.base_name == "pdata"
                )
                and "_" not in x.base_name
                and "." not in x.base_name
            ]
            selected_descriptors = result.descriptors
            if (
                dir_relative_path not in MANAGED_FOLDERS
                and required_raw_data_folder_files
                and optional_raw_data_folder_files
            ):
                logger.info(
                    "%s directory is raw data folder. Only fid*, ser* acqu* files will be added.",
                    dir_relative_path,
                )
                messages.append(
                    f"{dir_relative_path} directory is raw data folder. fid*, ser* acqu* files will be added."
                )
                selected_descriptors = required_raw_data_folder_files.copy()
                selected_descriptors.extend(
                    [x for x in optional_raw_data_folder_files if not x.is_directory]
                )
            for item in selected_descriptors:
                entry = item.base_name
                full_path: str = join_path(directory, entry).replace("\\", "/")
                relative_path = join_path(dir_relative_path, entry).replace("\\", "/")
                base_name = os.path.basename(relative_path)
                parent_directory = os.path.dirname(relative_path).replace("\\", "/")
                in_ignore_list = False
                for pattern in definitions.ignore_file_patterns:
                    if pattern.match(relative_path):
                        in_ignore_list = True
                        break
                if in_ignore_list:
                    logger.debug(
                        "%s directory is in content ignore list. SKIPPED",
                        relative_path,
                    )
                    messages.append(
                        f"{relative_path} directory is in content ignore list. SKIPPED"
                    )
                    continue

                descriptor = StudyFileDescriptor.model_validate(
                    item.model_dump(by_alias=True)
                )

                for tag in definitions.TAG_PATTERNS:
                    for pattern in definitions.TAG_PATTERNS[tag]:
                        if re.match(pattern, base_name, re.IGNORECASE):
                            descriptor.tags.append(tag)
                _, ext = os.path.splitext(relative_path)
                descriptor.extension = ext
                descriptor.parent_directory = parent_directory
                descriptor.file_path = relative_path

                metadata[relative_path] = descriptor
                if item.is_directory:
                    logger.debug("%s is directory, search content.", relative_path)
                    self.visit_folder(
                        full_path, study_path, metadata=metadata, messages=messages
                    )

        except Exception as exc:
            logger.exception("Directory error %s: %s", directory, str(exc))

    def get_folder_metadata(
        self,
        study_path,
        calculate_data_folder_size: bool = False,
        calculate_metadata_size: bool = False,
        metadata_files_only: bool = False,
        data_files_mapping_folder_name: None | str = None,
    ) -> Tuple[Union[None, StudyFolderMetadata], List[GenericMessage]]:
        study_folder_metadata = None
        metadata: Dict[str, StudyFileDescriptor] = {}
        messages: List[GenericMessage] = []
        current_file_index = None
        if os.path.exists(self.folder_index_file_path) and os.path.isfile(
            self.folder_index_file_path
        ):
            logger.info("%s file exists, loading...", self.folder_index_file_path)
            try:
                with open(self.folder_index_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    current_file_index = FolderIndex.model_validate(
                        data, from_attributes=True
                    )
                    study_folder_metadata = current_file_index.content
                    logger.info(
                        "%s file is loaded successfully.", self.folder_index_file_path
                    )
            except json.JSONDecodeError as ex:
                logger.error(
                    "%s json file decode error: %s",
                    self.folder_index_file_path,
                    str(ex),
                )
                msg = f"{self.folder_index_file_path} file decode error. {str(ex)}"
                messages.append(
                    GenericMessage(
                        type=GenericMessageType.WARNING,
                        short=msg,
                        detail=msg,
                    )
                )
            except Exception as ex:
                logger.exception(
                    "%s json file load error: %s",
                    self.folder_index_file_path,
                    str(ex),
                )
                msg = f"{self.folder_index_file_path} file load error. {str(ex)}"
                messages.append(
                    GenericMessage(
                        type=GenericMessageType.WARNING,
                        short=msg,
                        detail=msg,
                    )
                )

        if not study_folder_metadata or self.rebuild_folder_index_file:
            study_folder_metadata = StudyFolderMetadata()
            logger.info("Build study folder metadata index.")
            self.visit_folder(
                self.remote_study_directory,
                self.remote_study_directory,
                metadata=metadata,
                messages=messages,
            )
            study_folder_metadata.folders = {
                x: metadata[x] for x in metadata if metadata[x].is_directory
            }
            study_folder_metadata.files = {
                x: metadata[x] for x in metadata if not metadata[x].is_directory
            }

            now = datetime.datetime.now(datetime.timezone.utc)
            file_index = FolderIndex(update_time=now, content=study_folder_metadata)
            with open(self.folder_index_file_path, "w", encoding="utf-8") as fw:
                fw.write(file_index.model_dump_json(indent=4))
            msg = f"{self.folder_index_file_path} file is updated."
            logger.info(msg)
            messages.append(
                GenericMessage(
                    type=GenericMessageType.INFO,
                    short=msg,
                    detail=msg,
                )
            )
        else:
            msg = f"{self.folder_index_file_path} file is used."
            logger.info(msg)
            messages.append(
                GenericMessage(
                    type=GenericMessageType.INFO,
                    short=msg,
                    detail=msg,
                )
            )

        return (study_folder_metadata, messages)
