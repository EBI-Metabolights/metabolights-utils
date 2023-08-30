from humps import camelize
from pydantic import BaseModel


class CamelCaseModel(BaseModel):
    """Base model class to convert python attributes to camel case"""

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
