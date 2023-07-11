from typing import List

from metabolights_utils.models.isa.common import (
    IsaTableFile,
    OntologyItem,
    OrganismAndOrganismPartPair,
)


class SamplesFile(IsaTableFile):
    sampleNames: List[str] = []
    organisms: List[OntologyItem] = []
    organismParts: List[OntologyItem] = []
    organismAndOrganismPartPairs: List[OrganismAndOrganismPartPair] = []
    variants: List[OntologyItem] = []
    sampleTypes: List[OntologyItem] = []
