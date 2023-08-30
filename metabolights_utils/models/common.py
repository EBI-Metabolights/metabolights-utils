from metabolights_utils.common import CamelCaseModel
from metabolights_utils.models.enums import GenericMessageType


class MetabolightsBaseModel(CamelCaseModel):
    pass


class GenericMessage(MetabolightsBaseModel):
    type: GenericMessageType = GenericMessageType.ERROR
    short: str = ""
    detail: str = ""

    def __str__(self) -> str:
        value = f"{self.type}\tshort: {self.short}\tdetail: {self.detail}"
        return value
