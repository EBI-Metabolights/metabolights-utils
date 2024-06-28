import os
import re
from typing import List, Tuple, Union

import unidecode


class MetabolightsFileNameUtils(object):
    @staticmethod
    def sanitise_filename(
        filename: str,
        replacement_chars_pattern: Union[None, str] = None,
        allow_spaces: bool = False,
    ) -> str:
        if not filename or not filename.strip():
            return ""

        if not replacement_chars_pattern:
            replacement_chars_pattern = "[^/a-zA-Z0-9_.-]"
        filename = unidecode.unidecode(filename.strip())
        filename = filename.replace("+", "_PLUS_")
        if not allow_spaces:
            filename = "_".join(
                [x.strip() for x in filename.strip().split() if x.strip()]
            )

        filename = re.sub(replacement_chars_pattern, "_", filename)
        return filename


def join_path(*args: Tuple[str]):
    target_sep = "/" if os.sep == "/" else "\\"
    source_sep = "/" if os.sep == "\\" else "/"
    inputs = list([x for x in args if x and x.strip()])
    _path = target_sep.join(inputs).replace(source_sep, target_sep)
    return _path