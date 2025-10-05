import json
import os
from typing import Dict, Union

from metabolights_utils.models.metabolights import metabolights_study, model

default_version = "1.1"


def get_study_model_schema(
    schema_path: Union[str, None] = None, version: None | str = None
) -> Dict:
    if not schema_path:
        if version:
            filename = f"study_model_schema_v{version}.json"
        else:
            filename = f"study_model_schema_v{default_version}.json"
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(schema_path, "r", encoding="utf-8") as sf:
        study_model_jsonschema = json.load(sf)
    return study_model_jsonschema


__all__ = ["metabolights_study", "model", "get_study_model_schema"]
