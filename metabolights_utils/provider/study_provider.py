import json
import os
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Dict, List, Set, Union

from metabolights_utils.isatab.default.parser.investigation_parser import (
    parse_investigation_from_fs,
)
from metabolights_utils.isatab.default.parser.isa_table_parser import (
    assay_file_expected_patterns,
    parse_isa_table_sheet_from_fs,
    samples_file_expected_patterns,
)
from metabolights_utils.models.common import GenericMessage, GenericMessageType
from metabolights_utils.models.isa.assay_file import AssayFile
from metabolights_utils.models.isa.assignment_file import AssignmentFile
from metabolights_utils.models.isa.common import (
    AssayTechnique,
    IsaTableFile,
    OntologyItem,
    OrganismAndOrganismPartPair,
)
from metabolights_utils.models.isa.investigation_file import Investigation
from metabolights_utils.models.isa.samples_file import SamplesFile
from metabolights_utils.models.metabolights.model import (
    MetabolightsStudyModel,
    StudyDBMetadata,
    StudyFolderMetadata,
)
from metabolights_utils.models.parser.common import ParserMessage
from metabolights_utils.models.parser.enums import ParserMessageType

IGNORED_FILE_PATTERNS = {r"^AUDIT_FILES(/|$)(.*)", r"^INTERNAL_FILES(/|$)(.*)"}


STUDY_FIELDS = [
    "id",
    "acc",
    "obfuscationcode",
    "submissiondate",
    "releasedate",
    "updatedate",
    "studysize",
    "status_date",
    "studytype",
    "status",
    "override",
    "comment",
]

SUBMITTER_FIELDS = [
    "id",
    "orcid",
    "address",
    "joindate",
    "username",
    "firstname",
    "lastname",
    "status",
    "affiliation",
    "affiliationurl",
    "role",
]


class AbstractDbMetadataCollector(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_study_metadata_from_db(self, study_id: str, connection) -> StudyDBMetadata:
        pass


class AbstractFolderMetadataCollector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_folder_metadata(self, study_path) -> StudyFolderMetadata:
        pass


class MetabolightsStudyProvider(object):

    assay_technique_keywords: Dict[str, str] = {
        "Liquid Chromatography MS": "LC-MS",
        "Diode array detection MS": "LC-DAD",
        "Gas Chromatography MS": "GC-MS",
        "Tandem Gas Chromatography MS": "GCxGC-MS",
        "Flame ionisation detector MS": "GC-FID",
        "Mass spectrometry": "MS",
        "Direct infusion MS": "DI-MS",
        "Flow injection analysis MS": "FIA-MS",
        "Capillary electrophoresis MS": "CE-MS",
        "Matrix-assisted laser desorption-ionisation imaging MS": "MALDI-MS",
        "Solid-Phase Extraction Ion Mobility Spectrometry MS": "SPE-IMS-MS",
        "MS Imaging": "MSImaging",
        "Nuclear Magnetic Resonance (NMR)": "NMR",
        "Magnetic resonance imaging": "MRImaging",
    }

    assay_technique_labels: Dict[str, str] = {
        "LC-MS": "Liquid Chromatography MS",
        "LC-DAD": "Diode array detection MS",
        "GC-MS": "Gas Chromatography MS",
        "GCxGC-MS": "Tandem Gas Chromatography MS",
        "GC-FID": "Flame ionisation detector MS",
        "MS": "Mass spectrometry",
        "DI-MS": "Direct infusion MS",
        "FIA-MS": "Flow injection analysis MS",
        "CE-MS": "Capillary electrophoresis MS",
        "MALDI-MS": "Matrix-assisted laser desorption-ionisation imaging MS",
        "SPE-IMS-MS": "Solid-Phase Extraction Ion Mobility Spectrometry MS",
        "MSImaging": "MS Imaging",
        "NMR": "Nuclear Magnetic Resonance (NMR)",
        "MRImaging": "Magnetic resonance imaging",
    }

    manual_assignments = {
        "3D LAESI imaging MS": "MSImaging",
        "3D MALDI imaging MS": "MSImaging",
        "3D MALDI imaging MS simulation": "MSImaging",
        "3D MALDI imaging MS,3D DESI imaging MS": "MSImaging",
        "CE-TOF-MS": "CE-MS",
        "DI-FT-ICR-MS": "DI-MS",
        "DI-FT-ICR-MS/MS": "DI-MS",
        "DI-LTQ-MS": "DI-MS",
        "DI-LTQ-MS/MS": "DI-MS",
        "FIA-LTQ-MS": "FIA-MS",
        "FIA-LTQ-MS/MS": "FIA-MS",
        "FIA-MS": "FIA-MS",
        "FIA-QTOF-MS": "FIA-MS",
        "GC-Q-MS": "GC-MS",
        "GC-TOF-MS": "GC-MS",
        "HPLC-LTQ-MS": "LC-MS",
        "LC-LTQ-MS": "LC-MS",
        "LC-QTOF-MS": "LC-MS",
        "LC-TOF-MS": "LC-MS",
        "LC-TQ-MS": "LC-MS",
        "MALDI-TOF/TOF-MS": "MALDI-MS",
        "MS": "MS",
        "PTR-MS": "MS",
        "REI-QTOF-MS": "DI-MS",
        "SESI-LTQ-MS": "DI-MS",
        "SPE-IMS-MS": "LC-MS",
        "UPLC-LTQ-MS": "LC-MS",
        "UPLC-LTQ-MS/MS": "LC-MS",
        "UPLC-LTQ-MS/MS,UPLC-TQ-MS/MS": "LC-MS",
        "UPLC-MS/MS": "LC-MS",
        "UPLC-QTOF-MS": "LC-MS",
        "UPLC-QTOF-MS/MS": "LC-MS",
        "UPLC-TQ-MS": "LC-MS",
        "UPLC-TQ-MS MTBLS935 dupe?": "LC-MS",
        "UPLC-TQ-MS MTBLS936 dupe?": "LC-MS",
    }
    assay_techniques = {
        "LC-MS": AssayTechnique(
            name="LC-MS", mainTechnique="MS", technique="LC-MS", subTechnique="LC"
        ),
        "LC-DAD": AssayTechnique(
            name="LC-DAD", mainTechnique="MS", technique="LC-MS", subTechnique="LC-DAD"
        ),
        "GC-MS": AssayTechnique(
            name="GC-MS", mainTechnique="MS", technique="GC-MS", subTechnique="GC"
        ),
        "GCxGC-MS": AssayTechnique(
            name="GCxGC-MS",
            mainTechnique="MS",
            technique="GC-MS",
            subTechnique="Tandem (GCxGC)",
        ),
        "GC-FID": AssayTechnique(
            name="GC-FID", mainTechnique="MS", technique="GC-MS", subTechnique="GC-FID"
        ),
        "MS": AssayTechnique(
            name="MS",
            mainTechnique="MS",
            technique="Direct Injection",
            subTechnique="MS",
        ),
        "DI-MS": AssayTechnique(
            name="DI-MS",
            mainTechnique="MS",
            technique="Direct Injection",
            subTechnique="Direct infusion (DI)",
        ),
        "FIA-MS": AssayTechnique(
            name="FIA-MS",
            mainTechnique="MS",
            technique="Direct Injection",
            subTechnique="Flow injection analysis (FIA)",
        ),
        "CE-MS": AssayTechnique(
            name="CE-MS",
            mainTechnique="MS",
            technique="Direct Injection",
            subTechnique="Capillary electrophoresis (CE)",
        ),
        "MALDI-MS": AssayTechnique(
            name="MALDI-MS",
            mainTechnique="MS",
            technique="Direct Injection",
            subTechnique="Matrix-assisted laser desorption-ionisation imaging mass spectrometry (MALDI)",
        ),
        "SPE-IMS-MS": AssayTechnique(
            name="SPE-IMS-MS",
            mainTechnique="MS",
            technique="Direct Injection",
            subTechnique="Solid-Phase Extraction Ion Mobility Spectrometry (SPE-IMS)",
        ),
        "MSImaging": AssayTechnique(
            name="MSImaging",
            mainTechnique="MS",
            technique="MS Imaging",
            subTechnique="MS Imaging",
        ),
        "NMR": AssayTechnique(
            name="NMR",
            mainTechnique="NMR",
            technique="NMR",
            subTechnique="Nuclear magnetic resonance",
        ),
        "MRImaging": AssayTechnique(
            name="MRImaging",
            mainTechnique="NMR",
            technique="MRI",
            subTechnique="Magnetic resonance imaging",
        ),
    }

    def __init__(
        self,
        db_metadata_collector: Union[None, AbstractDbMetadataCollector] = None,
        folder_metadata_collector: Union[None, AbstractFolderMetadataCollector] = None,
    ) -> None:
        self.db_metadata_collector = db_metadata_collector
        self.folder_metadata_collector = folder_metadata_collector

    def _add_parse_messages(
        self,
        model: MetabolightsStudyModel,
        fileName: str,
        messages: List[ParserMessage],
    ):
        if fileName not in model.parser_messages:
            model.parser_messages[fileName] = []
        model.parser_messages[fileName].extend(self.filter_messages(messages))

    def get_unique_file_extensions(self, files: Set):
        extensions = set()

        for item in files:
            name1, ext1 = os.path.splitext(item)
            _, ext2 = os.path.splitext(name1)
            if ext1:
                if ext2 and len(ext2) < 5:
                    extensions.add(f"{ext2.lower()}{ext1.lower()}")
                else:
                    extensions.add(f"{ext1.lower()}")
        return extensions

    def find_assay_technique(
        self,
        model: MetabolightsStudyModel,
        assay_file: AssayFile,
        assay_file_subset: AssayFile,
    ):
        for study in model.investigation.studies:
            for assay in study.study_assays.assays:
                if assay.file_name == assay_file.file_path:
                    for technique in self.assay_technique_keywords:
                        if technique in assay.technology_platform:
                            return self.assay_techniques[
                                self.assay_technique_keywords[technique]
                            ]
        if (
            "NMR Assay Name" in assay_file.table.columns
            and "MS Assay Name" in assay_file.table.columns
        ):
            return AssayTechnique()

        if "NMR Assay Name" in assay_file.table.columns:
            if (
                "Parameter Value[Tomography]" in assay_file.table.columns
                and "Parameter Value[Magnetic pulse sequence name]"
                in assay_file.table.columns
            ):
                return self.assay_techniques["MRImaging"]
            else:
                return self.assay_techniques["NMR"]
        elif "MS Assay Name" in assay_file.table.columns:
            if "Parameter Value[DI Instrument]" in assay_file.table.columns:
                return self.assay_techniques["DI-MS"]
            elif "Parameter Value[FIA Instrument]" in assay_file.table.columns:
                return self.assay_techniques["FIA-MS"]
            elif "Parameter Value[CE Instrument]" in assay_file.table.columns:
                return self.assay_techniques["CE-MS"]
            elif (
                "Parameter Value[Column type 1]" in assay_file.table.columns
                and "Parameter Value[Column type 2]" in assay_file.table.columns
            ):
                return self.assay_techniques["GCxGC-MS"]
            elif "Parameter Value[SPE-IMS Instrument]" in assay_file.table.columns:
                return self.assay_techniques["SPE-IMS-MS"]
            elif "Thermal Desorption unit" in assay_file.table.columns:
                return self.assay_techniques["TD-GC-MS"]
            elif "Parameter Value[Sectioning instrument]" in assay_file.table.columns:
                return self.assay_techniques["MSImaging"]
            elif (
                "Parameter Value[Signal range]" in assay_file.table.columns
                and "Parameter Value[Resolution]" in assay_file.table.columns
            ):
                return self.assay_techniques["LC-DAD"]
            else:
                if "Parameter Value[Column type]" in assay_file_subset.table.columns:
                    if assay_file_subset.table.data["Parameter Value[Column type]"]:
                        values = assay_file_subset.table.data[
                            "Parameter Value[Column type]"
                        ]
                        for i in range(len(values) if len(values) < 3 else 3):
                            if values[i]:
                                columnType = values[i].lower()
                                if "hilic" in columnType or "reverse" in columnType:
                                    return self.assay_techniques["LC-MS"]
                                elif (
                                    "low polarity" in columnType
                                    or "high polarity" in columnType
                                    or "medium polarity" in columnType
                                ):
                                    return self.assay_techniques["GC-MS"]

            if model.study_db_metadata.study_types:
                study_type_str = ",".join(model.study_db_metadata.study_types)
                if study_type_str in self.manual_assignments:
                    manual_map = self.manual_assignments[study_type_str]
                    return self.assay_techniques[manual_map]

            if "_FIA" in assay_file.file_path:
                return self.assay_techniques["FIA-MS"]

        if model.investigation and model.investigation.studies:
            file_found = False
            for study_item in model.investigation.studies:
                if (
                    study_item
                    and study_item.study_assays
                    and study_item.study_assays.assays
                ):
                    for assay_item in study_item.study_assays.assays:
                        if assay_item.file_name == assay_file.file_path:
                            if "mass spectrometry" in assay_item.technology_type.term:
                                return self.assay_techniques["MS"]
                            elif "NMR spectrometry" in assay_item.technology_type.term:
                                return self.assay_techniques["NMR"]
                            file_found = True
                            break
                if file_found:
                    break
        return AssayTechnique()

    def set_organisms(self, samples_file: SamplesFile, table: SamplesFile):
        organism_set = set()
        organism_part_set = set()
        variant_set = set()

        sample_type_set = set()
        pairs = set()
        columns = table.table.columns
        data = table.table.data
        for i in range(samples_file.table.total_row_count):
            organism = ""
            organismPart = ""
            variant = ""
            if "Characteristics[Organism]" in columns:
                organism = data["Characteristics[Organism]"][i]

            sampleType = ""
            if "Characteristics[Sample type]" in columns:
                sampleType = data["Characteristics[Sample type]"][i]

            if "Characteristics[Organism part]" in columns:
                organismPart = data["Characteristics[Organism part]"][i]

            if "Characteristics[Variant]" in columns:
                variant = data["Characteristics[Variant]"][i]

            if organism:
                organism_term: OntologyItem = OntologyItem(
                    term=organism, term_source_ref="", term_accession_number=""
                )
                index = columns.index("Characteristics[Organism]")

                if index + 1 < len(columns) and columns[index + 1].startswith(
                    "Term Source REF"
                ):
                    organism_term.term_source_ref = data[columns[index + 1]][i]
                if index + 2 < len(columns) and columns[index + 2].startswith(
                    "Term Accession Number"
                ):
                    organism_term.term_accession_number = data[columns[index + 2]][i]
                    organism_set.add(organism_term)
            else:
                organism_term = OntologyItem()

            if organismPart:
                organismPartTerm: OntologyItem = OntologyItem(
                    term=organismPart, term_source_ref="", term_accession_number=""
                )
                index = columns.index("Characteristics[Organism part]")

                if index + 1 < len(columns) and columns[index + 1].startswith(
                    "Term Source REF"
                ):
                    organismPartTerm.term_source_ref = data[columns[index + 1]][i]
                if index + 2 < len(columns) and columns[index + 2].startswith(
                    "Term Accession Number"
                ):
                    organismPartTerm.term_accession_number = data[columns[index + 2]][i]
                organism_part_set.add(organismPartTerm)
            else:
                organismPartTerm = OntologyItem()

            if variant:
                variantTerm = OntologyItem(
                    term=variant, term_source_ref="", term_accession_number=""
                )
                index = columns.index("Characteristics[Variant]")

                if index + 1 < len(columns) and columns[index + 1].startswith(
                    "Term Source REF"
                ):
                    variantTerm.term_source_ref = data[columns[index + 1]][i]
                if index + 2 < len(columns) and columns[index + 2].startswith(
                    "Term Accession Number"
                ):
                    variantTerm.term_accession_number = data[columns[index + 2]][i]
                variant_set.add(variantTerm)
            else:
                variantTerm = OntologyItem()

            if sampleType:
                sampleTypeTerm = OntologyItem(
                    term=sampleType, term_source_ref="", term_accession_number=""
                )
                index = columns.index("Characteristics[Sample type]")

                if index + 1 < len(columns) and columns[index + 1].startswith(
                    "Term Source REF"
                ):
                    sampleTypeTerm.term_source_ref = data[columns[index + 1]][i]
                if index + 2 < len(columns) and columns[index + 2].startswith(
                    "Term Accession Number"
                ):
                    sampleTypeTerm.term_accession_number = data[columns[index + 2]][i]
                sample_type_set.add(sampleTypeTerm)
            else:
                sampleTypeTerm = OntologyItem()

            if organism_term.term:
                pairs.add(
                    OrganismAndOrganismPartPair(
                        organism=organism_term,
                        organismPart=organismPartTerm,
                        variant=variantTerm,
                        sampleType=sampleTypeTerm,
                    )
                )
        samples_file.organisms = list(organism_set)
        samples_file.organism_parts = list(organism_part_set)
        samples_file.variants = list(variant_set)
        samples_file.sample_types = list(sample_type_set)
        samples_file.organism_and_organism_part_pairs = list(pairs)

    def get_phase1_input_data(
        self, study_id: str, folder: Union[str, None] = None, connection=None
    ) -> MetabolightsStudyModel:
        model: MetabolightsStudyModel = MetabolightsStudyModel()

        self.update_investigation_file(model, folder)
        if self.db_metadata_collector and connection:
            self.update_study_db_metadata(
                model,
                self.db_metadata_collector,
                study_id=study_id,
                connection=connection,
            )

        if not model.investigation.studies:
            return model

        raw_files = set()
        derived_files = set()
        assignment_files = set()
        folders_in_hierarchy = set()
        investigation = model.investigation
        for study_item in investigation.studies:
            file_path = os.path.join(folder, study_item.file_name)
            samples_isa_table, messages = parse_isa_table_sheet_from_fs(
                file_path,
                samples_file_expected_patterns,
                limit=0,
                fix_unicode_exceptions=True,
            )
            self._add_parse_messages(model, study_item.file_name, messages)
            samples_file = SamplesFile()
            samples_file.file_path = study_item.file_name
            samples_file.table = samples_isa_table.table
            samples_file.sha256_hash = samples_isa_table.sha256_hash
            selected_column_names = set()

            selected_column_names = samples_isa_table.table.columns

            sample_names, message_list = parse_isa_table_sheet_from_fs(
                file_path,
                samples_file_expected_patterns,
                selected_columns=list(selected_column_names),
                fix_unicode_exceptions=True,
            )
            self._add_parse_messages(model, samples_file.file_path, message_list)

            samples_file.table.total_row_count = 0
            unique_sample_names = set()
            if sample_names.table.data and "Sample Name" in sample_names.table.data:
                samples_row = len(sample_names.table.data["Sample Name"])
                samples_file.table.total_row_count = samples_row

                unique_sample_names = {
                    f.strip() for f in sample_names.table.data["Sample Name"]
                }
            unique_sample_names.discard("")
            unique_sample_names.discard(None)
            samples_file.sample_names = list(unique_sample_names)
            self.set_organisms(samples_file, sample_names)
            model.samples[study_item.file_name] = samples_file
            for assay_item in study_item.study_assays.assays:
                file_path = os.path.join(folder, assay_item.file_name)
                assay_isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                    file_path,
                    assay_file_expected_patterns,
                    limit=0,
                    fix_unicode_exceptions=True,
                )
                assay_isa_table: IsaTableFile = assay_isa_table_sheet
                assay_file: AssayFile = AssayFile()
                assay_file.file_path = assay_item.file_name
                assay_file.table = assay_isa_table.table
                assay_file.sha256_hash = assay_isa_table.sha256_hash
                self._add_parse_messages(model, assay_item.file_name, messages)
                model.assays[assay_item.file_name] = assay_file

                selected_column_names = set()
                for column in assay_isa_table.table.columns:
                    if (
                        column.startswith("Raw Spectral Data File")
                        or column.startswith("Acquisition Parameter Data File")
                        or column.startswith("Free Induction Decay Data File")
                    ):
                        selected_column_names.add(column)
                    elif column.startswith("Derived Spectral Data File"):
                        selected_column_names.add(column)
                    elif column.startswith("Metabolite Assignment File"):
                        selected_column_names.add(column)
                    elif column == "Sample Name":
                        selected_column_names.add(column)
                    elif column == "MS Assay Name" or column == "NMR Assay Name":
                        selected_column_names.add(column)
                    elif column == "Parameter Value[Column type]":
                        selected_column_names.add(column)

                selected_column_names_list = list(selected_column_names)
                assay_file_subset_sheet, messages_list = parse_isa_table_sheet_from_fs(
                    file_path,
                    assay_file_expected_patterns,
                    selected_columns=selected_column_names_list,
                    fix_unicode_exceptions=True,
                )
                assay_file_subset: IsaTableFile = assay_file_subset_sheet
                self._add_parse_messages(model, assay_item.file_name, messages_list)
                if selected_column_names:
                    assay_file.table.total_row_count = 0
                    if assay_file_subset.table.data:
                        assay_file.table.total_row_count = len(
                            assay_file_subset.table.data[selected_column_names_list[0]]
                        )
                else:
                    column_names = assay_file.table.columns
                    if len(column_names) > 0:
                        (
                            first_column_of_table,
                            messages_list,
                        ) = parse_isa_table_sheet_from_fs(
                            file_path,
                            assay_file_expected_patterns,
                            selected_columns=[column_names[0]],
                            fix_unicode_exceptions=True,
                        )
                        first_column: IsaTableFile = first_column_of_table
                        self._add_parse_messages(
                            model, assay_item.file_name, messages_list
                        )
                        assay_file.table.total_row_count = 0
                        if first_column.table.data:
                            assay_file.table.total_row_count = len(
                                first_column.table.data[first_column.table.columns[0]]
                            )
                    else:
                        assay_file.table.total_row_count = 0
                    assay_file.table.row_count = 0
                assay_raw_files: Set = set()
                assay_raw_file_extensions: Set = set()
                assay_derived_files: Set = set()
                assay_derived_file_extensions = set()

                for column in assay_file_subset.table.columns:
                    file_set = {f.strip() for f in assay_file_subset.table.data[column]}
                    file_set.discard("")
                    file_set.discard(None)
                    file_list = list(file_set)
                    if (
                        column.startswith("Raw Spectral Data File")
                        or column.startswith("Acquisition Parameter Data File")
                        or column.startswith("Free Induction Decay Data File")
                    ):
                        raw_files.update(file_set)
                        assay_raw_files.update(file_list)
                        assay_raw_file_extensions.update(
                            self.get_unique_file_extensions(file_list)
                        )
                    elif column.startswith("Derived Spectral Data File"):
                        derived_files.update(file_set)
                        assay_derived_files.update(file_list)
                        assay_derived_file_extensions.update(
                            self.get_unique_file_extensions(file_list)
                        )
                    elif column.startswith("Metabolite Assignment File"):
                        assignment_files.update(file_set)
                        assay_file.referenced_assignment_files = file_list
                    elif column == "Sample Name":
                        assay_file.sample_names = file_list
                    elif column == "MS Assay Name" or column == "NMR Assay Name":
                        assay_file.assay_names = file_list
                assay_file.assay_technique = self.find_assay_technique(
                    model, assay_file, assay_file_subset
                )

                assay_file.referenced_raw_files = list(assay_raw_files)
                assay_file.referenced_derived_files = list(assay_derived_files)
                assay_file.referenced_raw_file_extensions = list(
                    assay_raw_file_extensions
                )
                assay_file.referenced_derived_file_extensions = list(
                    assay_derived_file_extensions
                )

        for set_item in (raw_files, derived_files, assignment_files):
            for item in set_item:
                if set_item != assignment_files:
                    folders_in_hierarchy.add(os.path.dirname(item))

        model.referenced_assignment_files.extend(list(assignment_files))
        model.referenced_raw_files.extend(list(raw_files))
        model.referenced_derived_files.extend(list(derived_files))
        model.folders_in_hierarchy.extend(list(folders_in_hierarchy))

        for assignment_file in assignment_files:
            absolute_path = os.path.join(folder, assignment_file)
            isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                absolute_path, limit=0, fix_unicode_exceptions=True
            )
            metabolite_assignment_isa_table: IsaTableFile = isa_table_sheet
            self._add_parse_messages(model, assignment_file, messages)
            file: AssignmentFile = AssignmentFile()
            file.file_path = assignment_file
            file.table = metabolite_assignment_isa_table.table
            file.sha256_hash = metabolite_assignment_isa_table.sha256_hash
            model.metabolite_assignments[assignment_file] = file
            column_names = file.table.columns

            selected_column_names = set()
            for column in file.table.columns:
                if (
                    column == "database_identifier"
                    or column == "metabolite_identification"
                ):
                    selected_column_names.add(column)

            if len(selected_column_names) > 0:
                selected_isa_table_data, messages_list = parse_isa_table_sheet_from_fs(
                    absolute_path,
                    selected_columns=list(selected_column_names),
                    fix_unicode_exceptions=True,
                )
                selected_column_values: IsaTableFile = selected_isa_table_data
                self._add_parse_messages(model, assignment_file, messages_list)

                file.table.total_row_count = 0
                metabolite_identifications = set()
                metabolite_assignments = {}
                if selected_column_values.table.data:
                    file.table.total_row_count = len(
                        selected_column_values.table.data[
                            selected_column_values.table.columns[0]
                        ]
                    )
                    for i in range(file.table.total_row_count):
                        database_identifier = ""
                        metabolite_identification = ""
                        for column in selected_column_names:
                            if column == "database_identifier":
                                database_identifier = selected_column_values.table.data[
                                    column
                                ][i]
                            elif column == "metabolite_identification":
                                metabolite_identification = (
                                    selected_column_values.table.data[column][i]
                                )
                        if metabolite_identification:
                            metabolite_identifications.add(metabolite_identification)
                            if database_identifier:
                                metabolite_assignments[metabolite_identification] = (
                                    database_identifier
                                )
                    file.identified_metabolite_names = list(metabolite_identifications)
                    file.metabolite_assignments = metabolite_assignments
                    file.number_of_assigned_rows = len(file.metabolite_assignments)
                    file.number_of_unassigned_rows = (
                        file.table.total_row_count - file.number_of_assigned_rows
                    )
                    file.number_of_rows = file.table.total_row_count
            else:
                file.table.total_row_count = 0
            file.table.row_count = 0

        for assay_file_name in model.assays:
            assay_file_item = model.assays[assay_file_name]
            for assignement_file_name in assay_file_item.referenced_assignment_files:
                model.metabolite_assignments[assignement_file_name].assay_technique = (
                    assay_file_item.assay_technique
                )
        return model

    def get_sample_file_input(
        self,
        study_id: str,
        folder: str,
        connection,
        samples_sheet_offset: Union[int, None] = None,
        samples_sheet_limit: Union[int, None] = None,
        model: MetabolightsStudyModel = None,
    ) -> MetabolightsStudyModel:
        if not model:
            model = self.get_phase1_input_data(study_id, folder, connection)

        for study_item in model.investigation.studies:
            file_path = os.path.join(folder, study_item.file_name)
            samples_isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                file_path,
                samples_file_expected_patterns,
                offset=samples_sheet_offset,
                limit=samples_sheet_limit,
                fix_unicode_exceptions=True,
            )
            samples_isa_table: IsaTableFile = samples_isa_table_sheet
            model.samples[study_item.file_name].table = samples_isa_table.table
            model.samples[study_item.file_name].sha256_hash = (
                samples_isa_table.sha256_hash
            )
            if samples_isa_table.table.data:
                model.samples[study_item.file_name].table.row_count = len(
                    samples_isa_table.table.data[samples_isa_table.table.columns[0]]
                )
            else:
                model.samples[study_item.file_name].table.row_count = 0

            model.parser_messages[study_item.file_name].extend(
                self.filter_messages(messages)
            )
            model.has_sample_table_data = True
        return model

    def get_phase2_input_data(
        self,
        study_id: str,
        folder: Union[None, str],
        connection=None,
        samples_sheet_offset: Union[int, None] = None,
        samples_sheet_limit: Union[int, None] = None,
        assay_sheet_offset: Union[int, None] = None,
        assay_sheet_limit: Union[int, None] = None,
        model: MetabolightsStudyModel = None,
    ) -> MetabolightsStudyModel:
        if not model:
            model = self.get_phase1_input_data(study_id, folder, connection)

        for study_item in model.investigation.studies:
            file_path = os.path.join(folder, study_item.file_name)
            samples_isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                file_path,
                samples_file_expected_patterns,
                offset=samples_sheet_offset,
                limit=samples_sheet_limit,
                fix_unicode_exceptions=True,
            )
            samples_isa_table: IsaTableFile = samples_isa_table_sheet
            model.samples[study_item.file_name].table = samples_isa_table.table
            model.samples[study_item.file_name].sha256_hash = (
                samples_isa_table.sha256_hash
            )

            if samples_isa_table.table.data:
                model.samples[study_item.file_name].table.row_count = len(
                    samples_isa_table.table.data[samples_isa_table.table.columns[0]]
                )
            else:
                model.samples[study_item.file_name].table.row_count = 0

            model.parser_messages[study_item.file_name].extend(
                self.filter_messages(messages)
            )
            for assay_item in study_item.study_assays.assays:
                file_path = os.path.join(folder, assay_item.file_name)
                assay_isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                    file_path,
                    assay_file_expected_patterns,
                    offset=assay_sheet_offset,
                    limit=assay_sheet_limit,
                    fix_unicode_exceptions=True,
                )
                assay_isa_table: IsaTableFile = assay_isa_table_sheet
                model.parser_messages[assay_item.file_name].extend(
                    self.filter_messages(messages)
                )
                model.assays[assay_item.file_name].table = assay_isa_table.table
                model.assays[assay_item.file_name].sha256_hash = (
                    assay_isa_table.sha256_hash
                )
                model.assays[assay_item.file_name].file_path = assay_isa_table.file_path
                if assay_isa_table.table.data:
                    model.assays[assay_item.file_name].table.row_count = len(
                        assay_isa_table.table.data[assay_isa_table.table.columns[0]]
                    )
                    model.assays[assay_item.file_name].number_of_assay_rows = (
                        model.assays[assay_item.file_name].table.row_count
                    )
                else:
                    model.assays[assay_item.file_name].table.row_count = 0
        if not samples_sheet_limit or samples_sheet_limit > 0:
            model.has_sample_table_data = True
        if not assay_sheet_limit or assay_sheet_limit > 0:
            model.has_assay_table_data = True
        return model

    def get_phase3_input_data(
        self,
        study_id: str,
        folder: str,
        connection,
        assignment_sheet_offset: Union[int, None] = None,
        assignment_sheet_limit: Union[int, None] = None,
        model: MetabolightsStudyModel = None,
    ) -> MetabolightsStudyModel:
        if not model:
            model = self.get_phase1_input_data(study_id, folder, connection)

        for assignment_file in model.metabolite_assignments:
            absolute_path = os.path.join(folder, assignment_file)
            (
                metabolite_assignment_isa_table_sheet,
                messages,
            ) = parse_isa_table_sheet_from_fs(
                absolute_path,
                offset=assignment_sheet_offset,
                limit=assignment_sheet_limit,
                fix_unicode_exceptions=True,
            )
            metabolite_assignment_isa_table: IsaTableFile = (
                metabolite_assignment_isa_table_sheet
            )
            model.parser_messages[assignment_file].extend(
                self.filter_messages(messages)
            )
            metabolite_assignment_isa_table.file_path = assignment_file
            model.metabolite_assignments[assignment_file].table = (
                metabolite_assignment_isa_table.table
            )
            model.metabolite_assignments[assignment_file].sha256_hash = (
                metabolite_assignment_isa_table.sha256_hash
            )
            model.metabolite_assignments[assignment_file].file_path = assignment_file

            if metabolite_assignment_isa_table.table.data:
                model.metabolite_assignments[assignment_file].table.row_count = len(
                    metabolite_assignment_isa_table.table.data[
                        metabolite_assignment_isa_table.table.columns[0]
                    ]
                )
            else:
                model.metabolite_assignments[assignment_file].table.row_count = 0
        if not assignment_sheet_limit or assignment_sheet_limit > 0:
            model.has_assignment_table_data = True

        return model

    def get_phase4_input_data(
        self,
        study_id: str,
        folder: Union[str, None] = None,
        connection=None,
        model: MetabolightsStudyModel = None,
    ) -> MetabolightsStudyModel:
        if not model:
            model = self.get_phase2_input_data(study_id, folder, connection)
        study_folder_metadata = self.folder_metadata_collector.get_folder_metadata(
            folder
        )
        model.study_folder_metadata = study_folder_metadata
        if folder:
            model.has_folder_metadata = True
        return model

    def filter_messages(self, messages: List[ParserMessage]):
        return [
            f
            for f in messages
            if f.type == ParserMessageType.CRITICAL
            or f.type == ParserMessageType.ERROR
            or f.type == ParserMessageType.WARNING
        ]

    def get_metabolights_study_model(
        self, study_id: str, folder: str, connection
    ) -> MetabolightsStudyModel:
        model = self.get_phase4_input_data(study_id, folder, connection)
        model = self.get_phase3_input_data(study_id, folder, connection, model=model)
        return model

    def load_study(
        self,
        study_id: str,
        study_path: str,
        connection=None,
        load_assay_files: bool = False,
        load_maf_files: bool = False,
        load_folder_metadata: bool = False,
        samples_sheet_offset: Union[int, None] = None,
        samples_sheet_limit: Union[int, None] = None,
        assay_sheet_offset: Union[int, None] = None,
        assay_sheet_limit: Union[int, None] = None,
        assignment_sheet_offset: Union[int, None] = None,
        assignment_sheet_limit: Union[int, None] = None,
    ) -> MetabolightsStudyModel:

        model = self.get_phase1_input_data(study_id, study_path, connection)

        if load_assay_files or load_folder_metadata:
            model = self.get_phase2_input_data(
                study_id,
                study_path,
                connection,
                model=model,
                samples_sheet_offset=samples_sheet_offset,
                samples_sheet_limit=samples_sheet_limit,
                assay_sheet_offset=assay_sheet_offset,
                assay_sheet_limit=assay_sheet_limit,
            )

        if load_folder_metadata:
            model = self.get_phase4_input_data(study_id, study_path, connection)

        if load_maf_files:
            model = self.get_phase3_input_data(
                study_id,
                study_path,
                connection,
                model=model,
                assignment_sheet_limit=assignment_sheet_limit,
                assignment_sheet_offset=assignment_sheet_offset,
            )
        return model

    def update_investigation_file(
        self, model: MetabolightsStudyModel, folder, file_name="i_Investigation.txt"
    ):
        file = os.path.join(folder, file_name)
        investigation, messages = parse_investigation_from_fs(
            file, fix_unicode_exceptions=True
        )
        if not investigation:
            investigation = Investigation()

        model.investigation_file_path = file_name
        model.investigation = investigation
        model.parser_messages[file_name] = self.filter_messages(messages)
        model.has_investigation_data = True
        return model

    def update_study_db_metadata(
        self,
        model: MetabolightsStudyModel,
        collector: AbstractDbMetadataCollector,
        study_id,
        connection,
    ):
        try:
            study_db_metadata = collector.get_study_metadata_from_db(
                study_id, connection
            )
            model.study_db_metadata = study_db_metadata
            model.has_assignment_table_data = True
        except Exception as ex:
            message = GenericMessage(
                type=GenericMessageType.ERROR,
                short=f"Error while reading database for {study_id} metadata",
                detail=f"{str(ex)}",
            )
            model.db_reader_messages.append(message)
        return model


if __name__ == "__main__":

    provider = MetabolightsStudyProvider()
    data = provider.load_study(
        "MTBLS1",
        study_path="tests/test-data/MTBLS1",
        load_assay_files=True,
        assay_sheet_limit=1,
    )
    print(data.parser_messages)
