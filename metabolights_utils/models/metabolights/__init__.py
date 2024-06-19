import json
import os
from typing import Dict, Union


def get_study_model_schema(schema_path: Union[str, None] = None) -> Dict:
    if not schema_path:
        schema_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "study_model_schema_v1.0.json",
        )
    with open(schema_path, "r", encoding="utf-8") as sf:
        study_model_jsonschema = json.load(sf)
    return study_model_jsonschema
