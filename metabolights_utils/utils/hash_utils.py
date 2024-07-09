import hashlib
import logging
import os
from typing import Dict

from pydantic import BaseModel

from metabolights_utils.utils.search_utils import MetabolightsSearchUtils as SearchUtils

logger = logging.getLogger(__name__)

EMPTY_FILE_HASH = hashlib.sha256("".encode()).hexdigest()


class IsaMetadataFolderHash(BaseModel):
    folder_sha256: str = ""
    files_sha256: Dict[str, str] = {}


class MetabolightsHashUtils(object):
    @staticmethod
    def sha256sum(filepath: str, convert_to_linux_line_ending: bool = True):
        if not filepath or not os.path.exists(filepath):
            logger.warning("Empty or invalid input file path %s", filepath)
            return EMPTY_FILE_HASH

        sha256_hash = hashlib.sha256()
        with open(filepath, mode="rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                if convert_to_linux_line_ending:
                    byte_block = byte_block.replace(b"\r\n", b"\n")
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def get_isa_metadata_folder_hash(folder_path: str) -> IsaMetadataFolderHash:
        files: list[str] = SearchUtils.get_isa_metadata_files(
            folder_path=folder_path, recursive=False
        )
        if not files:
            logger.warning("Empty or invalid input folder path %s", folder_path)
            return IsaMetadataFolderHash(folder_sha256=EMPTY_FILE_HASH)
        files.sort()
        result = IsaMetadataFolderHash()
        hashes = []
        for file in files:
            basename = os.path.basename(file)
            hash = MetabolightsHashUtils.sha256sum(file)
            result.files_sha256[basename] = hash
            hashes.append(f"{basename}:{hash}")
        hash_bytes = ",".join(hashes).encode("utf-8")
        result.folder_sha256 = hashlib.sha256(hash_bytes).hexdigest()
        logger.debug("Hash value of %s folder: %s", folder_path, result.folder_sha256)
        return result
