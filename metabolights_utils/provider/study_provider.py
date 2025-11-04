import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Set, Tuple, Union

from metabolights_utils.isatab.default.parser.investigation_parser import (
    parse_investigation_from_fs,
)
from metabolights_utils.isatab.default.parser.isa_table_parser import (
    assay_file_expected_patterns,
    parse_isa_table_sheet_from_fs,
    samples_file_expected_patterns,
)
from metabolights_utils.models.common import (
    CriticalMessage,
    GenericMessage,
    GenericMessageType,
)
from metabolights_utils.models.isa.assay_file import AssayFile
from metabolights_utils.models.isa.assignment_file import AssignmentFile
from metabolights_utils.models.isa.common import (
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
from metabolights_utils.provider.utils import (
    find_assay_technique,
    get_unique_file_extensions,
)

logger = logging.getLogger(__name__)


class AbstractMetadataFileProvider(ABC):
    @abstractmethod
    def get_study_metadata_path(
        self, study_id: str, file_relative_path: Union[None, str] = None
    ) -> str:
        pass

    @abstractmethod
    def exists(
        self, study_id: str, file_relative_path: Union[None, str] = None
    ) -> bool:
        pass


class DefaultStudyMetadataFileProvider(AbstractMetadataFileProvider):
    def __init__(self, study_metadata_root_path: str):
        self.study_metadata_root_path = study_metadata_root_path

    def get_study_metadata_path(
        self, study_id: str, file_relative_path: Union[None, str] = None
    ) -> str:
        if file_relative_path:
            return str(
                Path(self.study_metadata_root_path)
                / Path(study_id)
                / Path(file_relative_path)
            )

        else:
            return str(Path(self.study_metadata_root_path) / Path(study_id))

    def exists(
        self, study_id: str, file_relative_path: Union[None, str] = None
    ) -> bool:
        file_path = Path(self.get_study_metadata_path(study_id, file_relative_path))
        return file_path.resolve().exists()


class AbstractDbMetadataCollector(ABC):
    @abstractmethod
    def get_study_metadata_from_db(
        self, study_id: str, connection
    ) -> Tuple[Union[StudyDBMetadata, None], List[GenericMessage]]:
        """_summary_

        Args:
            study_id (str): MetaboLights study accession number.
            connection (Any): remote db connection to fetch study metadata.


        Returns:
            StudyDBMetadata: study metadata object
            that contains all the study db metadata fields.
            messages: List[GenericMessage]: list of messages
            to be populated with any errors or warnings.
        """


class AbstractFolderMetadataCollector(ABC):
    @abstractmethod
    def get_folder_metadata(
        self,
        study_path,
        calculate_data_folder_size: bool = False,
        calculate_metadata_size: bool = False,
        data_files_path: str = "FILES",
        data_files_mapping_folder_name: None | str = None,
    ) -> Tuple[Union[StudyFolderMetadata, None], List[GenericMessage]]:
        """_summary_

        Args:
            study_path (_type_): MetaboLights study metadata files path.
            calculate_data_folder_size (bool, optional): calculate study
            FILES folder size. Defaults to False.
            calculate_metadata_size (bool, optional): calculate size of
            study ISA metadata files
                even if they are referenced or not. Defaults to False.
                If calculate_data_folder_size and calculate_metadata_size are
                False, folder size will be set to -1.
            data_files_path: Current relative or absolute data files path.
                Default is "FILES"
            data_files_mapping_folder_name: Final data files folder on Public storage.
                Default is "FILES"
        Returns:
            StudyFolderMetadata: study folder metadata object that contains
            all descriptors of the study folders and files.
                .d, .raw and .m folders are included but not their content.
                If there is an error, None is returned.
            messages: List[GenericMessage]: list of messages to be populated
            with any errors or warnings.
        """


class MetabolightsStudyProvider:
    def __init__(
        self,
        db_metadata_collector: Union[None, AbstractDbMetadataCollector] = None,
        folder_metadata_collector: Union[None, AbstractFolderMetadataCollector] = None,
        metadata_file_provider: Union[None, AbstractMetadataFileProvider] = None,
    ) -> None:
        self.db_metadata_collector = db_metadata_collector
        self.folder_metadata_collector = folder_metadata_collector
        self.metadata_file_provider = metadata_file_provider

    def _add_parse_messages(
        self,
        model: MetabolightsStudyModel,
        fileName: str,
        messages: List[ParserMessage],
    ):
        if fileName not in model.parser_messages:
            model.parser_messages[fileName] = []
        model.parser_messages[fileName].extend(self.filter_messages(messages))

    def set_organisms(self, samples_file: SamplesFile, isa_table: SamplesFile):
        if (
            not samples_file
            or not samples_file.table
            or samples_file.table.total_row_count < 1
            or samples_file.table.total_column_count < 1
            or not samples_file.table.data
            or not samples_file.table.columns
        ):
            logger.warning(
                "Invalid sample file or there is no row or column in sample file. "
                "Skip to set organisms."
            )
            return
        pairs = set()
        columns = isa_table.table.columns
        data = isa_table.table.data
        characteristics_columns = [
            "Characteristics[Organism]",
            "Characteristics[Organism part]",
            "Characteristics[Variant]",
            "Characteristics[Sample type]",
        ]
        characteristics_set = {x: set() for x in characteristics_columns}
        source_ref_column_prefix = "Term Source REF"
        accession_column_prefix = "Term Accession Number"
        characteristics_column_indices = {
            x: columns.index(x) for x in characteristics_columns if x in columns
        }

        for i in range(len(data[columns[0]])):
            characteristics: Tuple[
                OntologyItem, OntologyItem, OntologyItem, OntologyItem
            ] = (OntologyItem(), OntologyItem(), OntologyItem(), OntologyItem())
            for idx, column_name in enumerate(characteristics_columns):
                if column_name not in characteristics_column_indices:
                    continue
                if column_name in columns:
                    characteristics[idx].term = data[column_name][i]
                index = characteristics_column_indices[column_name]
                source_ref = columns[index + 1] if index + 1 < len(columns) else ""

                if source_ref.startswith(source_ref_column_prefix):
                    characteristics[idx].term_source_ref = data[columns[index + 1]][i]
                accession = columns[index + 2] if index + 2 < len(columns) else ""

                if accession.startswith(accession_column_prefix):
                    characteristics[idx].term_accession_number = data[
                        columns[index + 2]
                    ][i]
                if characteristics[idx].term and characteristics[idx].term.strip():
                    characteristics_set[column_name].add(characteristics[idx])
            if characteristics[0].term and characteristics[0].term.strip():
                pairs.add(
                    OrganismAndOrganismPartPair(
                        organism=characteristics[0],
                        organismPart=characteristics[1],
                        variant=characteristics[2],
                        sampleType=characteristics[3],
                    )
                )
        samples_file.organisms = list(characteristics_set[characteristics_columns[0]])
        samples_file.organism_parts = list(
            characteristics_set[characteristics_columns[1]]
        )
        samples_file.variants = list(characteristics_set[characteristics_columns[2]])
        samples_file.sample_types = list(
            characteristics_set[characteristics_columns[3]]
        )
        samples_file.organism_and_organism_part_pairs = list(pairs)

    def get_file_path(
        self,
        relative_file_path: str,
        folder: Union[None, str],
        study_id: Union[None, str],
    ):
        if not folder:
            if not self.metadata_file_provider:
                raise ValueError("Define metadata file provider if folder is None.")
            file_path = self.metadata_file_provider.get_study_metadata_path(
                study_id, relative_file_path
            )
        else:
            file_path = Path(folder) / Path(relative_file_path)
        return str(file_path)

    def get_study_metadata_path(
        self,
        study_id: Union[None, str],
        folder: Union[None, str],
    ) -> Tuple[str, bool]:
        if not folder:
            study_path = self.metadata_file_provider.get_study_metadata_path(study_id)
            exist = self.metadata_file_provider.exists(study_id)
        else:
            file = Path(folder)
            study_path = folder
            real_path = file.resolve()
            exist = real_path.exists()
        return study_path, exist

    def get_phase1_input_data(
        self,
        study_id: str,
        folder: Union[str, None] = None,
        connection=None,
    ) -> MetabolightsStudyModel:
        model: MetabolightsStudyModel = MetabolightsStudyModel()
        logger.debug("Load i_Investigation.txt file on %s for %s", folder, study_id)
        self.update_investigation_file(model, folder, study_id=study_id)
        if self.db_metadata_collector and connection:
            logger.debug("Load %s study database metadata.", study_id)
            self.update_study_db_metadata(
                model,
                self.db_metadata_collector,
                study_id=study_id,
                connection=connection,
            )
        else:
            logger.debug("Skipped %s study database metadata.", study_id)
            message = GenericMessage(
                type=GenericMessageType.WARNING,
                short=f"Database metadata collection is skipped for {study_id}",
                detail=f"Database metadata collection is skipped for {study_id}",
            )
            model.db_reader_messages.append(message)

        if not model.investigation.studies:
            logger.warning(
                "There is no study definition in %s i_Investigation file.", study_id
            )
            return model

        raw_files = set()
        derived_files = set()
        assignment_files = set()
        folders_in_hierarchy = set()
        investigation = model.investigation
        for study_item in investigation.studies:
            file_path = self.get_file_path(study_item.file_name, folder, study_id)

            logger.debug("Load sample file headers %s", study_item.file_name)
            samples_isa_table, messages = parse_isa_table_sheet_from_fs(
                file_path,
                samples_file_expected_patterns,
                limit=0,
                fix_unicode_exceptions=True,
                remove_empty_rows=True,
                remove_new_lines_in_cells=True,
            )
            self._add_parse_messages(model, study_item.file_name, messages)
            samples_file = SamplesFile()
            samples_file.file_path = study_item.file_name
            samples_file.table = samples_isa_table.table
            samples_file.sha256_hash = samples_isa_table.sha256_hash
            selected_column_names = set()

            selected_column_names = samples_isa_table.table.columns
            logger.debug("Load sample file rows %s", study_item.file_name)

            sample_names, message_list = parse_isa_table_sheet_from_fs(
                file_path,
                samples_file_expected_patterns,
                selected_columns=list(selected_column_names),
                fix_unicode_exceptions=True,
                remove_empty_rows=True,
                remove_new_lines_in_cells=True,
            )
            self._add_parse_messages(model, samples_file.file_path, message_list)

            samples_file.table.total_row_count = 0
            logger.debug("Find unique sample names in sample file for %s.", study_id)

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
                file_path = self.get_file_path(assay_item.file_name, folder, study_id)

                logger.debug(
                    "Load %s assay file headers for %s.", assay_item.file_name, study_id
                )

                assay_isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                    file_path,
                    assay_file_expected_patterns,
                    limit=0,
                    fix_unicode_exceptions=True,
                    remove_empty_rows=True,
                    remove_new_lines_in_cells=True,
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
                logger.debug(
                    "Load %s selected assay file columns for %s.",
                    assay_item.file_name,
                    study_id,
                )
                selected_column_names_list = list(selected_column_names)
                assay_file_subset_sheet, messages_list = parse_isa_table_sheet_from_fs(
                    file_path,
                    assay_file_expected_patterns,
                    selected_columns=selected_column_names_list,
                    fix_unicode_exceptions=True,
                    remove_empty_rows=True,
                    remove_new_lines_in_cells=True,
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
                            remove_empty_rows=True,
                            remove_new_lines_in_cells=True,
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
                            get_unique_file_extensions(file_list)
                        )
                    elif column.startswith("Derived Spectral Data File"):
                        derived_files.update(file_set)
                        assay_derived_files.update(file_list)
                        assay_derived_file_extensions.update(
                            get_unique_file_extensions(file_list)
                        )
                    elif column.startswith("Metabolite Assignment File"):
                        assignment_files.update(file_set)
                        assay_file.referenced_assignment_files = file_list
                    elif column == "Sample Name":
                        assay_file.sample_names = file_list
                    elif column == "MS Assay Name" or column == "NMR Assay Name":
                        assay_file.assay_names = file_list
                assay_file.assay_technique = find_assay_technique(
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
                    folders_in_hierarchy.add(Path(item).parent.name)

        model.referenced_assignment_files.extend(list(assignment_files))
        model.referenced_raw_files.extend(list(raw_files))
        model.referenced_derived_files.extend(list(derived_files))
        model.folders_in_hierarchy.extend(list(folders_in_hierarchy))

        for assignment_file in assignment_files:
            absolute_path = self.get_file_path(assignment_file, folder, study_id)
            logger.debug(
                "Load %s assignment file  headers for %s.", assignment_file, study_id
            )
            isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                absolute_path,
                limit=0,
                fix_unicode_exceptions=True,
                remove_empty_rows=True,
                remove_new_lines_in_cells=True,
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
                    remove_empty_rows=True,
                    remove_new_lines_in_cells=True,
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
            for assignment_file_name in assay_file_item.referenced_assignment_files:
                model.metabolite_assignments[
                    assignment_file_name
                ].assay_technique = assay_file_item.assay_technique
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
            file_path = self.get_file_path(study_item.file_name, folder, study_id)
            samples_isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                file_path,
                samples_file_expected_patterns,
                offset=samples_sheet_offset,
                limit=samples_sheet_limit,
                fix_unicode_exceptions=True,
                remove_empty_rows=True,
                remove_new_lines_in_cells=True,
            )
            samples_isa_table: IsaTableFile = samples_isa_table_sheet
            model.samples[study_item.file_name].table = samples_isa_table.table
            model.samples[
                study_item.file_name
            ].sha256_hash = samples_isa_table.sha256_hash
            table = samples_isa_table.table
            table.row_count = 0
            if table.data:
                table.row_count = len(table.data[samples_isa_table.table.columns[0]])

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
            file_path = self.get_file_path(study_item.file_name, folder, study_id)

            samples_isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                file_path,
                samples_file_expected_patterns,
                offset=samples_sheet_offset,
                limit=samples_sheet_limit,
                fix_unicode_exceptions=True,
                remove_empty_rows=True,
                remove_new_lines_in_cells=True,
            )
            samples_isa_table: IsaTableFile = samples_isa_table_sheet
            model.samples[study_item.file_name].table = samples_isa_table.table
            model.samples[
                study_item.file_name
            ].sha256_hash = samples_isa_table.sha256_hash

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
                file_path = self.get_file_path(assay_item.file_name, folder, study_id)

                assay_isa_table_sheet, messages = parse_isa_table_sheet_from_fs(
                    file_path,
                    assay_file_expected_patterns,
                    offset=assay_sheet_offset,
                    limit=assay_sheet_limit,
                    fix_unicode_exceptions=True,
                    remove_empty_rows=True,
                    remove_new_lines_in_cells=True,
                )
                assay_isa_table: IsaTableFile = assay_isa_table_sheet
                model.parser_messages[assay_item.file_name].extend(
                    self.filter_messages(messages)
                )
                model.assays[assay_item.file_name].table = assay_isa_table.table
                model.assays[
                    assay_item.file_name
                ].sha256_hash = assay_isa_table.sha256_hash
                model.assays[assay_item.file_name].file_path = assay_isa_table.file_path
                if assay_isa_table.table.data:
                    model.assays[assay_item.file_name].table.row_count = len(
                        assay_isa_table.table.data[assay_isa_table.table.columns[0]]
                    )
                    model.assays[
                        assay_item.file_name
                    ].number_of_assay_rows = model.assays[
                        assay_item.file_name
                    ].table.row_count
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
            absolute_path = self.get_file_path(assignment_file, folder, study_id)
            (
                maf_isa_table_sheet,
                messages,
            ) = parse_isa_table_sheet_from_fs(
                absolute_path,
                offset=assignment_sheet_offset,
                limit=assignment_sheet_limit,
                fix_unicode_exceptions=True,
                remove_empty_rows=True,
                remove_new_lines_in_cells=True,
            )
            metabolite_assignment_isa_table: IsaTableFile = maf_isa_table_sheet
            model.parser_messages[assignment_file].extend(
                self.filter_messages(messages)
            )
            metabolite_assignment_isa_table.file_path = assignment_file
            model.metabolite_assignments[
                assignment_file
            ].table = metabolite_assignment_isa_table.table
            model.metabolite_assignments[
                assignment_file
            ].sha256_hash = metabolite_assignment_isa_table.sha256_hash
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
        calculate_data_folder_size: bool = False,
        calculate_metadata_size: bool = False,
        data_files_path: str = "FILES",
        data_files_mapping_folder_name: None | str = None,
    ) -> MetabolightsStudyModel:
        if not model:
            model = self.get_phase2_input_data(study_id, folder, connection)
        try:
            metadata, messages = self.folder_metadata_collector.get_folder_metadata(
                folder,
                calculate_data_folder_size=calculate_data_folder_size,
                calculate_metadata_size=calculate_metadata_size,
                data_files_path=data_files_path,
                data_files_mapping_folder_name=data_files_mapping_folder_name,
            )

            if messages:
                model.folder_reader_messages.extend(messages)
            if metadata:
                model.study_folder_metadata = metadata
                model.has_folder_metadata = True
        except Exception as ex:
            msg = f"Error while reading folder metadata: {str(ex)}"
            model.folder_reader_messages.append(
                GenericMessage(
                    type=GenericMessageType.ERROR,
                    short=msg,
                    detail=msg,
                )
            )
        return model

    def get_metabolights_study_model(
        self,
        study_id: str,
        folder: str,
        connection,
        load_sample_file: bool = True,
        load_assay_files: bool = True,
        load_maf_files: bool = True,
        load_folder_metadata: bool = True,
        samples_sheet_offset: Union[int, None] = None,
        samples_sheet_limit: Union[int, None] = None,
        assay_sheet_offset: Union[int, None] = None,
        assay_sheet_limit: Union[int, None] = None,
        assignment_sheet_offset: Union[int, None] = None,
        assignment_sheet_limit: Union[int, None] = None,
        calculate_data_folder_size: bool = False,
        calculate_metadata_size: bool = False,
    ) -> MetabolightsStudyModel:
        return self.load_study(
            study_id,
            folder,
            connection,
            load_sample_file=load_sample_file,
            load_assay_files=load_assay_files,
            load_maf_files=load_maf_files,
            load_folder_metadata=load_folder_metadata,
            samples_sheet_offset=samples_sheet_offset,
            samples_sheet_limit=samples_sheet_limit,
            assay_sheet_offset=assay_sheet_offset,
            assay_sheet_limit=assay_sheet_limit,
            assignment_sheet_offset=assignment_sheet_offset,
            assignment_sheet_limit=assignment_sheet_limit,
            calculate_data_folder_size=calculate_data_folder_size,
            calculate_metadata_size=calculate_metadata_size,
        )

    def load_study(
        self,
        study_id: str,
        study_path: str,
        connection=None,
        load_sample_file: bool = False,
        load_assay_files: bool = False,
        load_maf_files: bool = False,
        load_folder_metadata: bool = False,
        samples_sheet_offset: Union[int, None] = None,
        samples_sheet_limit: Union[int, None] = None,
        assay_sheet_offset: Union[int, None] = None,
        assay_sheet_limit: Union[int, None] = None,
        assignment_sheet_offset: Union[int, None] = None,
        assignment_sheet_limit: Union[int, None] = None,
        calculate_data_folder_size: bool = False,
        calculate_metadata_size: bool = False,
        data_files_path: str = "FILES",
        data_files_mapping_folder_name: None | str = None,
    ) -> MetabolightsStudyModel:
        if not study_id:
            raise ValueError("invalid study_id")
        exist = False
        study_path, exist = self.get_study_metadata_path(study_id, study_path)

        if not study_path:
            raise ValueError("invalid study_path")
        if not exist:
            model = MetabolightsStudyModel()
            message = CriticalMessage(
                short=f"Study folder does not exist for {study_id} {study_path}"
            )
            model.folder_reader_messages.append(message)
            return model

        model = self.get_phase1_input_data(study_id, study_path, connection)
        if load_sample_file and not load_assay_files and not load_folder_metadata:
            model = self.get_sample_file_input(
                study_id,
                study_path,
                connection,
                model=model,
                samples_sheet_offset=samples_sheet_offset,
                samples_sheet_limit=samples_sheet_limit,
            )

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
            model = self.get_phase4_input_data(
                study_id,
                study_path,
                connection=connection,
                model=model,
                calculate_data_folder_size=calculate_data_folder_size,
                calculate_metadata_size=calculate_metadata_size,
                data_files_path=data_files_path,
                data_files_mapping_folder_name=data_files_mapping_folder_name,
            )
        else:
            message = GenericMessage(
                type=GenericMessageType.WARNING,
                short=f"Folder metadata collection is skipped for {study_id}",
                detail=f"Folder metadata collection is skipped for {study_id}",
            )
            model.folder_reader_messages.append(message)

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
        self,
        model: MetabolightsStudyModel,
        folder,
        file_name="i_Investigation.txt",
        study_id: Union[None, str] = None,
    ):
        file = self.get_file_path(file_name, folder, study_id)
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
            study_db_metadata, messages = collector.get_study_metadata_from_db(
                study_id, connection
            )
            if messages:
                model.db_reader_messages.extend(messages)
            if study_db_metadata:
                model.study_db_metadata = study_db_metadata
                model.has_db_metadata = True
        except Exception as ex:
            logger.exception("Error while reading datadata for %s", study_id)
            message = GenericMessage(
                type=GenericMessageType.ERROR,
                short=f"Error while reading database for {study_id} metadata",
                detail=f"{str(ex)}",
            )
            model.db_reader_messages.append(message)
        return model

    def filter_messages(self, messages: List[ParserMessage]):
        return [
            f
            for f in messages
            if f.type == ParserMessageType.CRITICAL
            or f.type == ParserMessageType.ERROR
            or f.type == ParserMessageType.WARNING
        ]
