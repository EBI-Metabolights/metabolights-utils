import os

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """Base model class to convert python attributes to camel case"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
    )


def sort_by_study_id(key: str):
    if key:
        val = os.path.basename(key).upper().replace("MTBLS", "")
        if val.isnumeric():
            value = int(val)
            return value if value > 0 else -1
    return -1
