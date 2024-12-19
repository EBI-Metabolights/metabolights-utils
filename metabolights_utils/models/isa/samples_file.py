from typing import List

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.isa.common import (
    IsaTableFile,
    OntologyItem,
    OrganismAndOrganismPartPair,
)


class SamplesFile(IsaTableFile):
    sample_names: Annotated[
        List[str],
        Field(description="Unique values in `Sample Name` column in the sample file."),
    ] = []
    organisms: Annotated[
        List[OntologyItem],
        Field(description="Unique organism values in the sample file."),
    ] = []
    organism_parts: Annotated[
        List[OntologyItem],
        Field(description="Unique organism part values in the sample file."),
    ] = []
    organism_and_organism_part_pairs: Annotated[
        List[OrganismAndOrganismPartPair],
        Field(
            description="Unique organism, organism part, variant and sample type values in the sample file."
        ),
    ] = []
    variants: Annotated[
        List[OntologyItem],
        Field(description="Unique variant values in the sample file."),
    ] = []
    sample_types: Annotated[
        List[OntologyItem],
        Field(description="Unique sample type values in the sample file."),
    ] = []
