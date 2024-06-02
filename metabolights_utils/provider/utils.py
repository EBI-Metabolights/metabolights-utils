import json


def get_study_model_schema(schema_path: str):
    with open(schema_path, "r", encoding="utf-8") as sf:
        study_model_jsonschema = json.load(sf)
    return study_model_jsonschema
