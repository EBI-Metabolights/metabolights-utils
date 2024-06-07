from typing_extensions import Annotated

from pydantic import Field

from metabolights_utils.common import CamelCaseModel
from metabolights_utils.models.enums import GenericMessageType


class MetabolightsBaseModel(CamelCaseModel):
    pass


class GenericMessage(MetabolightsBaseModel):
    type: Annotated[GenericMessageType, Field(description="")] = (
        GenericMessageType.ERROR
    )
    short: Annotated[str, Field(description="")] = ""
    detail: Annotated[str, Field(description="")] = ""

    def __str__(self) -> str:
        value = f"{self.type}\tshort: {self.short}\tdetail: {self.detail}"
        return value


class InfoMessage(GenericMessage):
    type: Annotated[GenericMessageType, Field(description="")] = GenericMessageType.INFO


class WarningMessage(GenericMessage):
    type: Annotated[GenericMessageType, Field(description="")] = (
        GenericMessageType.WARNING
    )


class CriticalMessage(GenericMessage):
    type: Annotated[GenericMessageType, Field(description="")] = (
        GenericMessageType.CRITICAL
    )


class ErrorMessage(GenericMessage):
    type: Annotated[GenericMessageType, Field(description="")] = (
        GenericMessageType.ERROR
    )
