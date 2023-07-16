from typing import List

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.parser.enums import ParserMessageType


class ParserMessage(MetabolightsBaseModel):
    type: ParserMessageType = ParserMessageType.WARNING
    short: str = ""
    detail: str = ""
    section: str = ""
    line: str = ""
    column: str = ""

    def __str__(self) -> str:
        return "\t".join(
            [
                self.type,
                f"section: {self.section}",
                f"line: {self.line}",
                f"column: {self.column}",
                self.short,
                f"detail: {self.detail}",
            ]
        )


class ParserReport(MetabolightsBaseModel):
    messages: List[ParserMessage] = []
