from typing import List

from metabolights_utils.isatab.default.base_isa_table_file import BaseIsaTableFileReader


class DefaultAssayFileReader(BaseIsaTableFileReader):
    patterns = [
        [r"^(Extract Name)$", ""],
        [r"^(Protocol REF)(.\d+)?$", "Protocol"],
        [r"^(Sample Name)$", ""],
        [r"^Parameter Value[(\w[ -~]*)]$", "Parameter Value"],
        [r"^Comment\b[(\w{1}[ -~]*)]$", "Comment"],
        [r"^(Labeled Extract Name)$", ""],
        [r"^(Label)$", ""],
    ]

    def __init__(self, results_per_page=100) -> None:
        super().__init__(results_per_page=results_per_page)

    def _get_expected_patterns(self) -> List[List[str]]:
        return DefaultAssayFileReader.patterns
