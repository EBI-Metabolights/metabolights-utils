import glob
import os
from typing import List


class MetabolightsSearchUtils(object):
    @staticmethod
    def get_isa_metadata_files(folder_path: str, recursive=False) -> List[str]:
        metadata_files = []
        patterns = ["[asi]_*.txt", "m_*.tsv"]
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return metadata_files

        for pattern in patterns:
            search_pattern = os.path.join(folder_path, pattern)
            metadata_files.extend(glob.glob(search_pattern, recursive=recursive))
        return metadata_files
