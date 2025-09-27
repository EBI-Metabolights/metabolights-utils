import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MetabolightsSearchUtils:
    @staticmethod
    def get_isa_metadata_files(folder_path: str, recursive: bool = False) -> list[str]:
        metadata_files = []
        patterns = ["[asi]_*.txt", "m_*.tsv"]
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            logger.warning("Not valid directory %s", folder_path)
            return metadata_files

        for pattern in patterns:
            if recursive:
                metadata_files.extend(folder.rglob(pattern))
            else:
                metadata_files.extend(list(folder.glob(pattern)))
        return metadata_files
