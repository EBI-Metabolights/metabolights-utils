import os
from typing import Union

import click

from metabolights_utils.provider import definitions
from metabolights_utils.provider.submission_repository import (
    MetabolightsSubmissionRepository,
)

VALID_PARAMETERS = {
    "LC-MS": (
        {"positive", "negative", "alternating"},
        {"hilic", "reverse phase", "direct infusion"},
    ),
    "LC-DAD": (
        {"positive", "negative", "alternating"},
        {"hilic", "reverse phase", "direct infusion"},
    ),
    "GC-MS": ({"positive"}, {}),
    "GCxGC-MS": ({"positive"}, {}),
    "GC-FID": ({"positive"}, {}),
    "DI-MS": ({}, {}),
    "FIA-MS": ({}, {}),
    "CE-MS": ({}, {}),
    "MALDI-MS": ({}, {}),
    "MSImaging": ({}, {}),
    "NMR": ({}, {}),
}


@click.command(no_args_is_help=True, name="create-assay")
@click.option(
    "--local_path",
    "-p",
    default=definitions.default_local_submission_root_path,
    help="Local storage root path. Folder will be created if it does not exist.",
)
@click.option(
    "--rest_api_base_url",
    "-u",
    default=definitions.default_rest_api_url,
    help="MetaboLights study submission API base URL.",
)
@click.option(
    "--local_cache_path",
    "-x",
    default=definitions.default_local_submission_cache_path,
    help="Path to store cache files of study submission file indices, study models, etc.",
)
@click.option(
    "--credentials_file_path",
    "-c",
    default=definitions.default_local_submission_credentials_file_path,
    help="Path to store cache files of study submission file indices, study models, etc.",
)
@click.option(
    "--scan_polarity",
    "--polarity",
    help="Scan polarity of the assay.",
)
@click.option(
    "--column_type",
    help="Column type of the assay.",
)
@click.argument("study_id")
@click.argument("assay_technique")
def submission_create_assay(
    study_id: str = "",
    assay_technique: str = "",
    local_path: Union[None, str] = None,
    local_cache_path: Union[None, str] = None,
    rest_api_base_url: Union[None, str] = None,
    override_local_files: bool = False,
    credentials_file_path: str = "",
    scan_polarity: str = "",
    column_type: str = "",
):
    """
    Creates a study assay and maf file.

    study_id: MetaboLights study accession number (MTBLSxxxx).
    assay_technique: Valid assay techniques:  NMR, LC-MS, LC-DAD, GC-MS, GCxGC-MS, GC-FID, DI-MS, FIA-MS, CE-MS, MALDI-MS, MSImaging

    Acronyms: Diode array detection (LC-DAD), Tandem MS (GCxGC-MS), Flame ionisation detector (GC-FID),
    Direct infusion (DI-MS), Flow injection analysis (FIA-MS), Capillary electrophoresis (CE-MS),
    Matrix-assisted laser desorption-ionisation imaging mass spectrometry (MALDI-MS),
    Nuclear magnetic resonance (NMR), Mass spec spectrometry (MSImaging)



    scan_polarity (optional): Valid only for LC-MS, LC-DAD, GC-MS, GCxGC-MS, GC-FID. Valid values: positive, negative, alternating


    column_type (optional): Valid only for LC-MS, LC-DAD. Valid values: hilic, reverse phase, direct infusion
    """
    study_id = study_id.upper().strip()
    # assay_technique = assay_technique.upper().strip() if assay_technique else ""
    if assay_technique not in VALID_PARAMETERS:
        click.echo(f"Invalid assay technique: {assay_technique}")
        return
    if scan_polarity and scan_polarity not in VALID_PARAMETERS[assay_technique][0]:
        valid_message = f"{', '.join(VALID_PARAMETERS[assay_technique][0])}"
        if not valid_message:
            valid_message = "There is no scan polarity option for this assay technique. Do not use this parameter option."
        else:
            valid_message = f"Valid scan polarity values are: {valid_message}."
        click.echo(
            f"Invalid scan polarity parameter '{scan_polarity}' for assay technique {assay_technique}. {valid_message}"
        )
        return

    if column_type and column_type not in VALID_PARAMETERS[assay_technique][1]:
        valid_message = f"{', '.join(VALID_PARAMETERS[assay_technique][1])}"
        if not valid_message:
            valid_message = "There is no column type option for this assay technique. Do not use this parameter option."
        else:
            valid_message = f"Valid column types are: {valid_message}."
        click.echo(
            f"Invalid column type  parameter '{column_type}' for assay technique {assay_technique}. {valid_message}"
        )
        return

    client = MetabolightsSubmissionRepository(
        local_storage_root_path=local_path,
        local_storage_cache_path=local_cache_path,
        rest_api_base_url=rest_api_base_url,
        credentials_file_path=credentials_file_path,
    )
    assay_filename, maf_filename, error = client.create_assay(
        study_id=study_id,
        assay_technique=assay_technique,
        scan_polarity=scan_polarity,
        column_type=column_type,
    )
    if not assay_filename:
        click.echo(error)
        return
    else:
        click.echo(
            f"Created files for study {study_id}: {assay_filename} and {maf_filename}"
        )

    result = client.download_submission_metadata_files(
        study_id=study_id,
        override_local_files=override_local_files,
        delete_unlisted_metadata_files=False,
    )
    study_path = os.path.join(client.local_storage_root_path, study_id)
    click.echo(f"Download submission study {study_id} on {study_path} status:")
    for item in result.actions:
        click.echo(f"  {result.actions[item]}\t{item}")


if __name__ == "__main__":
    submission_create_assay(["MTBLS5397", "DI-MS"])
