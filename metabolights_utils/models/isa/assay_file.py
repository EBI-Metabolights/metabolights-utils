from typing import List

from metabolights_utils.models.isa.common import AssayTechnique, IsaTableFile


class AssayFile(IsaTableFile):
    sampleNames: List[str] = []
    assayNames: List[str] = []
    referencedAssignmentFiles: List[str] = []
    referencedRawFiles: List[str] = []
    referencedDerivedFiles: List[str] = []

    referencedRawFileExtensions: List[str] = []
    referencedDerivedFileExtensions: List[str] = []
    assayTechnique: AssayTechnique = AssayTechnique()
    numberOfAssayRows: int = 0
