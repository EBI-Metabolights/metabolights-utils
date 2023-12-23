from metabolights_utils.models.isa.assay_file import AssayFile
from metabolights_utils.models.isa.assignment_file import AssignmentFile
from metabolights_utils.models.isa.samples_file import SamplesFile
from metabolights_utils.models.metabolights.metabolights_study import (
    BaseMetabolightsStudyModel,
)


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
