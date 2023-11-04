from pydantic import ConfigDict, BaseModel
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """Base model class to convert python attributes to camel case"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
