from typing import List

from metabolights.isatab.default.base_isa_table_file import BaseIsaTableFileReader


class DefaultAssayFileReader(BaseIsaTableFileReader):
    patterns = [
        [r"^(Extract Name)$", ""],
        [r"^(Protocol REF)(.\d+)?$", "Protocol"],
        [r"^(Sample Name)$", ""],
        [r"^[ ]*Parameter[ ]+Value[ ]*\[[ ]*(\w[ -~]*)[ ]*\][ ]*$", "Parameter Value"],
        [r"^[ ]*Comment[ ]*\[[ ]*(\w[ -~]*)[ ]*\][ ]*$", "Comment"],
        [r"^(Labeled Extract Name)$", ""],
        [r"^(Label)$", ""],
    ]

    def __init__(self, results_per_page=100) -> None:
        super().__init__(results_per_page=results_per_page)

    def get_expected_patterns(self) -> List[List[str]]:
        return DefaultAssayFileReader.patterns
