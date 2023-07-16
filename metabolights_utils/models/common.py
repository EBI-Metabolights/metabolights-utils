from pydantic import BaseModel, Field

from metabolights_utils.models.enums import GenericMessageType


class MetabolightsBaseModel(BaseModel):
    pass


class GenericMessage(MetabolightsBaseModel):
    type: GenericMessageType = GenericMessageType.ERROR
    short: str = ""
    detail: str = ""

    def __str__(self) -> str:
        value = f"{self.type}\short: {self.short}\tdetail: {self.detail}"
        return value
