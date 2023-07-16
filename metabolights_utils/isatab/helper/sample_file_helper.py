from typing import List

from metabolights_utils.isatab.helper.base_isa_table_file_helper import BaseIsaTableFileHelper


class SampleFileHelper(BaseIsaTableFileHelper):
    patterns = [
        ["^(Source Name)$", ""],
        ["^Characteristics\[(\w[ -~]*)\]$", "Characteristics"],
        ["^(Protocol REF)(\.\d+)?$", "Protocol"],
        ["^(Sample Name)$", ""],
        ["^Factor Value\[(\w[ -~]*)\]$", "Factor Value"],
        ["^Comment\b\[(\w{1}[ -~]*)\]$", "Comment"],
    ]

    def __init__(self, results_per_page=100) -> None:
        super().__init__(results_per_page=results_per_page)

    def _get_expected_patterns(self) -> List[List[str]]:
        return SampleFileHelper.patterns
