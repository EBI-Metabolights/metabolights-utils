# import json

from jsonschema import validate

from metabolights_utils.models.isa.assay_file import AssayFile
from metabolights_utils.models.isa.assignment_file import AssignmentFile
from metabolights_utils.models.isa.samples_file import SamplesFile
from metabolights_utils.models.metabolights import get_study_model_schema
from metabolights_utils.models.metabolights.metabolights_study import (
    BaseMetabolightsStudyModel,
)
from metabolights_utils.models.metabolights.model import MetabolightsStudyModel
from metabolights_utils.provider.study_provider import MetabolightsStudyProvider


def test_create_metabolights_study_02():
    base_metabolights = BaseMetabolightsStudyModel()
    sample_file = SamplesFile()
    assay_file = AssayFile()
    assignment_file = AssignmentFile()
    base_metabolights.assays["a_x.txt"] = assay_file
    base_metabolights.samples["s_x.txt"] = sample_file
    base_metabolights.referenced_assignment_files.append(assignment_file)

    assert len(base_metabolights.assays) == 1
    assert len(base_metabolights.samples) == 1


def test_get_schema():
    result = get_study_model_schema()
    assert result
    provider = MetabolightsStudyProvider()

    model: MetabolightsStudyModel = provider.load_study(
        "MTBLS1",
        "tests/test-data/MTBLS1",
        connection=None,
        load_assay_files=True,
        load_sample_file=True,
        load_maf_files=True,
        load_folder_metadata=True,
        calculate_data_folder_size=True,
        calculate_metadata_size=True,
    )
    try:
        # schema = MetabolightsStudyModel.model_json_schema(
        #     by_alias=True, mode="serialization"
        # )
        # with open("schema.json", "w") as f:
        #     json.dump(schema, f, indent=4)
        validate(model.model_dump(by_alias=True), result)
    except Exception as x:
        raise AssertionError(f"schema validation failed. {str(x)}")
