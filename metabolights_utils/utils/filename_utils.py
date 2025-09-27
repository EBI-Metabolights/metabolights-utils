import logging
import os
import re
from typing import Union

import unidecode

logger = logging.getLogger(__name__)


class MetabolightsFileNameUtils:
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
        new_filename = unidecode.unidecode(filename.strip())
        new_filename = new_filename.replace("+", "_PLUS_")
        if not allow_spaces:
            new_filename = "_".join(
                [x.strip() for x in new_filename.strip().split() if x.strip()],
            )

        new_filename = re.sub(replacement_chars_pattern, "_", new_filename)
        if new_filename != filename:
            logger.debug("'%s' is converted to '%s'", filename, new_filename)
        return new_filename


def join_path(*args: tuple[str]):
    target_sep = "/" if os.sep == "/" else "\\"
    source_sep = "/" if os.sep == "\\" else "/"
    inputs = [x for x in args if x and x.strip()]
    path_ = target_sep.join(inputs).replace(source_sep, target_sep)
    return path_
