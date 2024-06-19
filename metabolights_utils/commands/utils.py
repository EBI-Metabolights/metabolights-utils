import io
import re
from typing import Callable, List

from bs4 import BeautifulSoup

from metabolights_utils.models.enums import GenericMessageType
from metabolights_utils.models.isa.common import IsaTable
from metabolights_utils.models.isa.investigation_file import Study
from metabolights_utils.models.metabolights.model import MetabolightsStudyModel
from metabolights_utils.models.parser.enums import ParserMessageType


def sub_arrays(arr: List[str], k: int):
    if k <= 0:
        raise ValueError("k must be greater than 0")

    array_list = []
    if not arr:
        return array_list
    arr.sort()
    count = 0
    current_list = None
    for item in arr:
        if count % k == 0:
            current_list = []
            array_list.append(current_list)
        current_list.append(item)
        count += 1
    return array_list


def find_column_names(isa_table: IsaTable, pattern: str):
    column_names = []
    if not isa_table or not isa_table.columns:
        return column_names
    if not pattern or not pattern.strip():
        return isa_table.columns
    column_names = [x for x in isa_table.columns if re.match(pattern, x)]
    return column_names


def get_unique_values(values: List[str]) -> List[str]:
    if not values:
        return []
    value_set = set([x.strip() for x in values if x and x.strip()])
    unique_values = list(value_set)
    unique_values.sort()
    return unique_values


def convert_html_to_plain_text(text: str):
    if not text:
        return ""
    f = io.BytesIO(bytes(text, encoding="utf-8"))
    soup = BeautifulSoup(f, "html.parser")
    return soup.text


def split_to_lines(text: str, max_line_size=120, sep=None, join_term=None):
    if not text or not text.strip():
        return []

    join_term = join_term if join_term else " "
    join_term_len = len(join_term)
    words = text.split(sep) if sep else text.split()

    count = 0
    array_list = []
    current_list = []
    for word in words:
        word = " ".join(word.split())
        if count + len(word) + join_term_len > max_line_size:
            array_list.append(join_term.join(current_list))
            current_list = []
            count = 0
        current_list.append(word.strip())
        count += len(word) + join_term_len if count > 0 else len(word)
    if current_list:
        array_list.append(join_term.join(current_list).strip())
    return array_list


assay_column_search_patterns = [
    r".*Parameter.+Value.*\[.+\].*",
    r".*Metabolite.*Assignment.*File.*",
]


def print_study_model_summary(model: MetabolightsStudyModel, log: Callable = print):
    if (
        not model
        or not log
        or not model.investigation
        or not model.investigation_file_path
        or not model.investigation.studies
        or not model.investigation.studies[0]
    ):
        return

    study: Study = model.investigation.studies[0]
    study_id = study.identifier
    log(f"{study.identifier}: {study.title}")
    public_date = study.public_release_date
    submission_date = study.submission_date
    contacts = study.study_contacts.people
    lines = split_to_lines(convert_html_to_plain_text(study.description))
    for line in lines:
        log(f"\t{line}")
    log(f"\nRelease Date\t: {public_date}\nSubmission Date\t: {submission_date}")
    submitters = ", ".join([f"{x.first_name} {x.last_name}" for x in contacts])
    log(f"Submitter(s)\t: {submitters}\n")
    descriptors = study.study_design_descriptors.design_types
    descriptor_format = "\n".join([f"\t- {str(x)}" for x in descriptors])
    log(f"\nDescriptors:\n{descriptor_format}")
    factors = study.study_factors.factors
    factors_format = "\n".join([f"\t- {str(x)}" for x in factors])
    log(f"Factors:\n{factors_format}")

    protocols = study.study_protocols.protocols
    log("Protocols:")
    for protocol in protocols:
        lines = split_to_lines(convert_html_to_plain_text(protocol.description))
        log(f"\t- {protocol.name}")
        for line in lines:
            log(f"\t\t{line}")

    if model.assays:
        log("\nAssays:")
    for _, assay in model.assays.items():
        report: List[str] = []
        report.append(f"- {assay.file_path}")
        report.append(
            f"Row count: {assay.table.total_row_count} Column Count: {assay.table.total_column_count}"
        )
        report.append(f"Technique: {assay.assay_technique}")
        report.append(f"Raw Files: {len(assay.referenced_raw_files)}")
        raw_extensions = assay.referenced_raw_file_extensions
        report.append(f"Raw File Extensions: {', '.join(raw_extensions)}")
        report.append(f"Derived Files: {len(assay.referenced_derived_files)}")
        derived_extensions = assay.referenced_derived_file_extensions
        report.append(f"Derived File Extensions: {', '.join(derived_extensions)}")
        assignments = assay.referenced_assignment_files
        print_columns(report, assay.table, assay_column_search_patterns, indent_tab=3)
        stats = "\n\t\t- ".join(report)
        log(f"\t{stats}")

    if model.metabolite_assignments:
        log("\nMetabolite Assignment Files (MAF):")
    for _, maf in model.metabolite_assignments.items():
        report: List[str] = []
        report.append(f"- {maf.file_path}")
        report.append(f"Row count: {maf.number_of_rows}")
        report.append(f"Main technique: {maf.assay_technique.main_technique}")
        report.append(f"Annotated metabolites: {len(maf.metabolite_assignments)}")
        stats = "\n\t\t- ".join(report)
        log(f"\t{stats}")

        if maf.metabolite_assignments:
            log("\t\t- Metabolite Annotations:")
            assignments = [
                f"{maf.metabolite_assignments[x]}:{x}"
                for x in maf.metabolite_assignments
            ]
            lines = split_to_lines(
                convert_html_to_plain_text(", ".join(assignments)), sep=", "
            )
            for line in lines:
                log(f"\t\t\t{line}")
        else:
            log("\t\t- Metabolite Annotations: - ")

    log("\nSample File:")
    sample_filepath = study.file_name
    sample_file = model.samples[sample_filepath]
    report = []
    patterns = [r".*Characteristics.*\[.+\].*", r".*Factor.+Value.*\[.+\].*"]
    print_columns(report, sample_file.table, patterns, indent_tab=2)
    stats = "\n\t- ".join(report)
    log(f"\t- {stats}")
    log("")

    errors = []
    for file, messages in model.parser_messages.items():
        for message in messages:
            if message.type in (ParserMessageType.CRITICAL, ParserMessageType.ERROR):
                errors.append(f"{study_id} {file}: {message.short}")
    for message in model.db_reader_messages:
        if message.type in (GenericMessageType.CRITICAL, GenericMessageType.ERROR):
            errors.append(f"{study_id} DB: {message.short}\t{message.detail}")
    for message in model.folder_reader_messages:
        if message.type in (GenericMessageType.CRITICAL, GenericMessageType.ERROR):
            errors.append(f"{study_id} Folder: {message.short}\t{message.detail}")
    if errors:
        log("Model Errors:")
        for error in errors:
            lines = split_to_lines(error)
            for line in lines:
                log(f"\t- {line}")


def print_columns(
    report: List[str],
    isa_table: IsaTable,
    patterns: List[str],
    indent_tab=2,
    max_item_in_row=6,
):
    tab = "\t" * indent_tab
    for pattern in patterns:
        column_names = find_column_names(isa_table, pattern)
        for colum_name in column_names:
            unique_values = get_unique_values(isa_table.data[colum_name])
            if unique_values:
                if len(unique_values) < 6:
                    report.append(f"{colum_name}: {', '.join(unique_values)}")
                else:
                    arrays = sub_arrays(unique_values, max_item_in_row)
                    terms = []
                    for array in arrays:
                        terms.append(f"{', '.join(array)}")
                    joined_terms = "- " + f"\n{tab}- ".join(terms)
                    report.append(f"{colum_name}:\n{tab}{joined_terms}")
            else:
                report.append(f"{colum_name}: -")
