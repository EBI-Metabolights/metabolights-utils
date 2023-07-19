from typing import List

from metabolights_utils.models.isa.common import (
    IsaTableFile,
    OntologyItem,
    OrganismAndOrganismmPartPair,
)


class SamplesFile(IsaTableFile):
    sample_names: List[str] = []
    organisms: List[OntologyItem] = []
    organism_parts: List[OntologyItem] = []
    organism_and_organism_part_pairs: List[OrganismAndOrganismmPartPair] = []
    variants: List[OntologyItem] = []
    sample_types: List[OntologyItem] = []
