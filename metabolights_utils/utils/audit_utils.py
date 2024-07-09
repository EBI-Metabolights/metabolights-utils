import datetime
import logging
import os
import shutil
from typing import Union

from metabolights_utils.utils.filename_utils import join_path
from metabolights_utils.utils.search_utils import MetabolightsSearchUtils as SearchUtils

logger = logging.getLogger(__name__)


class MetabolightsAuditUtils(object):

    @staticmethod
    def create_audit_folder(
        src_root_path: str,
        target_root_path: str,
        folder_suffix: Union[None, str] = "BACKUP",
        folder_prefix: Union[None, str] = None,
        timestamp_format: str = "%Y-%m-%d_%H-%M-%S",
    ) -> Union[None, str]:
        if not timestamp_format or not src_root_path or not target_root_path:
            logger.error("Invalid input parameter.")
            return None
        base = datetime.datetime.now(datetime.timezone.utc).strftime(timestamp_format)
        folder_name = f"{base}_{folder_suffix}" if folder_suffix else base
        folder_name = f"{folder_prefix}_{folder_name}" if folder_prefix else folder_name
        logger.info("Audit folder name: %s", folder_name)
        target_folder_path = join_path(target_root_path, folder_name)
        return MetabolightsAuditUtils.copy_isa_metadata_files(
            src_folder_path=src_root_path,
            target_folder_path=target_folder_path,
        )

    @staticmethod
    def copy_isa_metadata_files(
        src_folder_path: str, target_folder_path: str
    ) -> Union[None, str]:
        real_src_folder_path = os.path.realpath(src_folder_path)
        real_target_folder_path = os.path.realpath(target_folder_path)
        metadata_files_list = SearchUtils.get_isa_metadata_files(
            folder_path=real_src_folder_path, recursive=False
        )
        metadata_files_list.sort()

        if metadata_files_list:
            if not os.path.exists(real_target_folder_path):
                os.makedirs(real_target_folder_path, exist_ok=True)
                logger.info("Target folder is created: %s", target_folder_path)
            for file in metadata_files_list:
                basename = os.path.basename(file)
                target_file = join_path(target_folder_path, basename)
                shutil.copy2(file, target_file, follow_symlinks=False)
            logger.info(
                "Metadata files are copied from %s to %s",
                src_folder_path,
                target_folder_path,
            )
            return target_folder_path
        logger.warning("There is no metadata file on %s", src_folder_path)
        return None
