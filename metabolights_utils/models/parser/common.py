from typing import List

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.common import MetabolightsBaseModel
from metabolights_utils.models.parser.enums import ParserMessageType


class ParserMessage(MetabolightsBaseModel):
    type: Annotated[
        ParserMessageType,
        Field(
            description="Message type. Valid values: INFO, WARNING, ERROR, CRITICAL."
        ),
    ] = ParserMessageType.WARNING
    short: Annotated[str, Field(description="Short information about message.")] = ""
    detail: Annotated[str, Field(description="Detailed information about message.")] = (
        ""
    )
    section: Annotated[
        str, Field(description="Section name if it is i_Investigation.txt file")
    ] = ""
    line: Annotated[
        str,
        Field(
            description="File line number. It is valid only for i_Investigation.txt file."
        ),
    ] = ""
    column: Annotated[str, Field(description="ISA file table column name.")] = ""

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
