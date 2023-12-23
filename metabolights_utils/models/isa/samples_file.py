from typing import List

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.isa.common import (
    IsaTableFile,
    OntologyItem,
    OrganismAndOrganismPartPair,
)


class SamplesFile(IsaTableFile):
    sample_names: Annotated[List[str], Field(description="")] = []
    organisms: Annotated[List[OntologyItem], Field(description="")] = []
    organism_parts: Annotated[List[OntologyItem], Field(description="")] = []
    organism_and_organism_part_pairs: Annotated[
        List[OrganismAndOrganismPartPair], Field(description="")
    ] = []
    variants: Annotated[List[OntologyItem], Field(description="")] = []
    sample_types: Annotated[List[OntologyItem], Field(description="")] = []
