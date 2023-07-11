from metabolights_utils.models.isa.common import IsaAbstractModel
from metabolights_utils.models.isa.enums import GenericMessageType, ParserMessageType


class GenericMessage(IsaAbstractModel):
    type: GenericMessageType = GenericMessageType.ERROR
    short: str = ""
    detail: str = ""

    def __str__(self) -> str:
        value = f"{self.type}\short: {self.short}\tdetail: {self.detail}"
        return value


class ParserMessage(IsaAbstractModel):
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
