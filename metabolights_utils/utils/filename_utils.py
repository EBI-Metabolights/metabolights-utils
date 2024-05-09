import re

import unidecode


def sanitise_filename(
    filename: str,
    replacement_chars_pattern: None | str = None,
    allow_spaces: bool = False,
) -> str:
    if not filename or not filename.strip():
        return ""

    if not replacement_chars_pattern:
        replacement_chars_pattern = "[^/a-zA-Z0-9_.-]"
    filename = unidecode(filename.strip())
    filename = filename.replace("+", "_PLUS_")
    if not allow_spaces:
        filename = "".join([x.strip() for x in filename.strip().split() if x.strip()])

    filename = re.sub(replacement_chars_pattern, "_", filename)
    return filename
