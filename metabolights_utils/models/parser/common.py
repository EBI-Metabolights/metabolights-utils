from typing import List

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.parser.enums import ParserMessageType


class ParserMessage(MetabolightsBaseModel):
    type: Annotated[ParserMessageType, Field(description="")] = (
        ParserMessageType.WARNING
    )
    short: Annotated[str, Field(description="")] = ""
    detail: Annotated[str, Field(description="")] = ""
    section: Annotated[
        str, Field(description="Section name if it is investigation file")
    ] = ""
    line: Annotated[str, Field(description="")] = ""
    column: Annotated[str, Field(description="")] = (
        "Column name in ISA metadata table file"
    )

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
    messages: Annotated[List[ParserMessage], Field(description="")] = []
