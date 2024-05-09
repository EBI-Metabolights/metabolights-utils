import os
import shutil
from datetime import time

from metabolights_utils.utils.search_utils import get_isa_metadata_files


def create_audit_folder(
    src_root_folder: str,
    target_root_path: str,
    folder_suffix: None | str = "BACKUP",
    folder_prefix: None | str = None,
    timestamp_format: str = "%Y-%m-%d_%H-%M-%S",
    override_target_folder: bool = False,
) -> None | str:
    metadata_files_list = get_isa_metadata_files(
        folder_path=src_root_folder, recursive=False
    )
    metadata_files_list.sort()

    if metadata_files_list:
        base = time.strftime(timestamp_format)
        folder_name = f"{base}_{folder_suffix}" if folder_suffix else base
        folder_name = f"{folder_prefix}_{folder_name}" if folder_suffix else folder_name

        target_folder_path = os.path.join(target_root_path, folder_name)
        if override_target_folder and os.path.exists(target_folder_path):
            shutil.rmtree(target_folder_path)
            os.makedirs(target_folder_path)
        else:
            os.makedirs(target_folder_path, exist_ok=True)

        for file in metadata_files_list:
            basename = os.path.basename(file)
            target_file = os.path.join(target_folder_path, basename)
            shutil.copy2(file, target_file, follow_symlinks=True)
        return target_folder_path
    return None
