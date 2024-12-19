from typing import List

from metabolights_utils.isatab.default.base_isa_table_file import BaseIsaTableFileReader


class DefaultSampleFileReader(BaseIsaTableFileReader):
    patterns = [
        [r"^[ ]*(Source Name)[ ]*$", ""],
        [r"^[ ]*Characteristics[ ]*\[[ ]*(\w[ -~]*)[ ]*\](.\d+)?$", "Characteristics"],
        [r"^[ ]*(Protocol REF)[ ]*(.\d+)?[ ]*$", "Protocol"],
        [r"^[ ]*(Sample Name)[ ]*$", ""],
        [r"^[ ]*Factor[ ]+Value[ ]*\[[ ]*(\w[ -~]*)[ ]*\](.\d+)?$", "Factor Value"],
        [r"^[ ]*Comment[ ]*\[[ ]*(\w[ -~]*)[ ]*\](.\d+)?$", "Comment"],
    ]

    def __init__(self, results_per_page=100) -> None:
        super().__init__(results_per_page=results_per_page)

    def get_expected_patterns(self) -> List[List[str]]:
        return DefaultSampleFileReader.patterns
