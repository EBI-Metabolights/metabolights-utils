import re
from pathlib import Path

home = str(Path.home())
default_ftp_server_url = "ftp.ebi.ac.uk"
default_remote_repository_root_directory = "/pub/databases/metabolights/studies/public"
default_local_repository_root_path = f"{home}/metabolights_data/studies/data"
default_local_submission_root_path = f"{home}/metabolights_data/submission/data"
default_local_submission_cache_path = f"{home}/metabolights_data/submission/cache"
default_local_submission_credentials_file_path = (
    f"{home}/metabolights_data/submission/credentials/.login"
)
default_local_repority_cache_path = f"{home}/metabolights_data/studies/cache"
default_rest_api_url = "https://www.ebi.ac.uk/metabolights/ws"
default_validation_api_url = "https://www.ebi.ac.uk/metabolights/ws3"
default_study_search_rest_api_url = "https://www.ebi.ac.uk/metabolights/ws3"
default_private_ftp_server_url = "ftp-private.ebi.ac.uk"

IGNORED_FILE_PATTERNS = {r"^AUDIT_FILES(/|$)(.*)", r"^INTERNAL_FILES(/|$)(.*)"}

SKIP_FOLDER_CONTENT_PATTERNS = {
    r"^FILES/.+\.d(/|$)(.*)",
    r"^FILES/.+\.raw(/|$)(.*)",
    r"^FILES/.+\.m(/|$)(.*)",
}

ignore_file_patterns = [re.compile(x, re.IGNORECASE) for x in IGNORED_FILE_PATTERNS]
skip_folder_content_patterns = [
    re.compile(x, re.IGNORECASE) for x in SKIP_FOLDER_CONTENT_PATTERNS
]

COMPRESSED_FILE_EXTENSIONS = [
    ".zip",
    ".zipx",
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


COMPRESSED_FILE_PATTERNS = {r"^[\w].*" + f"({'|'.join(COMPRESSED_FILE_EXTENSIONS)})$"}

TAG_PATTERNS = {
    "type:hidden_file": {r"^\..*$"},
    "type:isatab_file/assay": {r"^a_[\w].*\.txt$"},
    "type:isatab_file/samples": {r"^s_[\w].*\.txt$"},
    "type:isatab_file/investigation": {r"^i_[\w].*\.txt$"},
    "type:isatab_file/assignments": {r"^m_[\w].*\.tsv$"},
    "type:compressed_file": COMPRESSED_FILE_PATTERNS,
    "type:internal_file": {
        r"^validation_files.json.*$",
        r"^validation_report.json.*$",
        r"^metexplore_mapping.json.*$",
        r"^missing_files.txt.*$",
        r"^files-all.json.*",
    },
}
