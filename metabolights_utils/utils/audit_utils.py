import datetime
import os
import shutil
from typing import Union

from metabolights_utils.utils.search_utils import MetabolightsSearchUtils as SearchUtils


class MetabolightsAuditUtils(object):

    @staticmethod
    def create_audit_folder(
        src_root_path: str,
        target_root_path: str,
        folder_suffix: Union[None, str] = "BACKUP",
        folder_prefix: Union[None, str] = None,
        timestamp_format: str = "%Y-%m-%d_%H-%M-%S",
    ) -> Union[None, str]:
        metadata_files_list = SearchUtils.get_isa_metadata_files(
            folder_path=src_root_path, recursive=False
        )
        metadata_files_list.sort()

        if metadata_files_list:
            base = datetime.datetime.now(datetime.timezone.utc).strftime(
                timestamp_format
            )
            folder_name = f"{base}_{folder_suffix}" if folder_suffix else base
            folder_name = (
                f"{folder_prefix}_{folder_name}" if folder_prefix else folder_name
            )

            target_folder_path = os.path.join(target_root_path, folder_name)

            os.makedirs(target_folder_path, exist_ok=True)

            for file in metadata_files_list:
                basename = os.path.basename(file)
                target_file = os.path.join(target_folder_path, basename)
                shutil.copy2(file, target_file, follow_symlinks=False)
            return target_folder_path
        return None

    @staticmethod
    def copy_isa_metadata_files(
        src_folder_path: str, target_folder_path: str
    ) -> Union[None, str]:
        metadata_files_list = SearchUtils.get_isa_metadata_files(
            folder_path=src_folder_path, recursive=False
        )
        metadata_files_list.sort()

        if metadata_files_list:
            os.makedirs(target_folder_path, exist_ok=True)
            for file in metadata_files_list:
                basename = os.path.basename(file)
                target_file = os.path.join(target_folder_path, basename)
                shutil.copy2(file, target_file, follow_symlinks=False)
            return target_folder_path
        return None
