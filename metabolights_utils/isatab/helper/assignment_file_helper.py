from typing import List

from metabolights_utils.isatab.helper.base_isa_table_file_helper import BaseIsaTableFileHelper


class AssignmentFileHelper(BaseIsaTableFileHelper):
    patterns = [
        ["^(datdatabase_identifier)$", ""],
        ["^(chemical_formula)$", ""],
        ["^(smiles)$", ""],
        ["^(inchi)$", ""],
        ["^(metabolite_identification)$", ""],
        ["^(mass_to_charge)$", ""],
        ["^(fragmentation)$", ""],
        ["^(modifications)$", ""],
        ["^(charge)$", ""],
        ["^(retention_time)$", ""],
        ["^(taxid)$", ""],
        ["^(chemical_shift)$", ""],
        ["^(multiplicity)$", ""],
        ["^(species)$", ""],
        ["^(database)$", ""],
        ["^(database_version)$", ""],
        ["^(reliability)$", ""],
        ["^(uri)$", ""],
        ["^(search_engine)$", ""],
        ["^(search_engine_score)$", ""],
        ["^(smallmolecule_abundance_sub)$", ""],
        ["^(smallmolecule_abundance_stdev_sub)$", ""],
        ["^(smallmolecule_abundance_std_error_sub)$", ""],
    ]

    def __init__(self, results_per_page=100) -> None:
        super().__init__(results_per_page=results_per_page)

    def _get_expected_patterns(self) -> List[List[str]]:
        return AssignmentFileHelper.patterns
