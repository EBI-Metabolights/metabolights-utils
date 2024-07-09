import glob
import logging
import os
from typing import List

logger = logging.getLogger(__name__)

from metabolights_utils.utils.filename_utils import join_path


class MetabolightsSearchUtils(object):
    @staticmethod
    def get_isa_metadata_files(folder_path: str, recursive: bool = False) -> List[str]:
        metadata_files = []
        patterns = ["[asi]_*.txt", "m_*.tsv"]
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            logger.warning("Not valid directory %s", folder_path)
            return metadata_files

        for pattern in patterns:
            search_pattern = join_path(folder_path, pattern)
            metadata_files.extend(glob.glob(search_pattern, recursive=recursive))
        return metadata_files
