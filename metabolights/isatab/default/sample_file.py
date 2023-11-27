from typing import List

from metabolights.isatab.default.base_isa_table_file import BaseIsaTableFileReader


class DefaultSampleFileReader(BaseIsaTableFileReader):
    patterns = [
        [r"^[ ]*(Source Name)[ ]*$", ""],
        [r"^[ ]*Characteristics[ ]*\[[ ]*(\w[ -~]*)[ ]*\][ ]*$", "Characteristics"],
        [r"^[ ]*(Protocol REF)[ ]*(.\d+)?[ ]*$", "Protocol"],
        [r"^[ ]*(Sample Name)[ ]*$", ""],
        [r"^[ ]*Factor[ ]+Value[ ]*\[[ ]*(\w[ -~]*)[ ]*\][ ]*$", "Factor Value"],
        [r"^[ ]*Comment[ ]*\[[ ]*(\w[ -~]*)[ ]*\][ ]*$", "Comment"],
    ]

    def __init__(self, results_per_page=100) -> None:
        super().__init__(results_per_page=results_per_page)

    def get_expected_patterns(self) -> List[List[str]]:
        return DefaultSampleFileReader.patterns
