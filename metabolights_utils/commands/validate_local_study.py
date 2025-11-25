import json
import subprocess
from pathlib import Path

import click

from metabolights_utils.commands.utils import download_file
from metabolights_utils.models.metabolights.model import MetabolightsStudyModel
from metabolights_utils.provider.local_folder_metadata_collector import (
    LocalFolderMetadataCollector,
)
from metabolights_utils.provider.study_provider import MetabolightsStudyProvider
from metabolights_utils.provider.submission_model import (
    OpaValidationResult,
    PolicyMessageType,
)


@click.command(no_args_is_help=True, name="local-validate")
@click.option(
    "--data_files_path",
    required=False,
    help="The data files root path.",
    type=click.Path(exists=True),
)
@click.option(
    "--output_directory",
    required=False,
    help="Output file directory.",
    default=".mtbls-validation-outputs",
)
@click.option(
    "--overridden_rules_file_path",
    required=False,
    help="A txt file that contains a validation rule identifier in each row."
    " e.g. one row: rule_i_100_350_003_01. All validation errors listed in this file "
    " will be filtered from the result.",
    type=click.Path(exists=True),
)
@click.option(
    "--mtbls_validation_bundle_path",
    required=False,
    help="Location of MetaboLights validation bundle path. "
    "You can download the latest one on "
    "https://raw.githubusercontent.com/EBI-Metabolights/mtbls-validation/refs/heads/test/docs/bundle.tar.gz",
    default="bundle.tar.gz",
)
@click.option(
    "--refetch_mtbls_validation_bundle",
    required=False,
    is_flag=True,
    help="A flag to enable remote validation of the study. "
    "You can download the latest one on "
    "https://raw.githubusercontent.com/EBI-Metabolights/mtbls-validation/refs/heads/test/docs/bundle.tar.gz",
    default=False,
)
@click.option(
    "--mtbls_validation_bundle_url",
    required=False,
    help="URL to download validation bundle.",
    default="https://raw.githubusercontent.com/EBI-Metabolights/mtbls-validation/refs/heads/test/docs/bundle.tar.gz",
)
@click.option(
    "--opa_executable_path",
    required=False,
    help="OPA executable path.",
    default="opa",
)
@click.argument("mtbls_provisional_study_id")
@click.argument("metadata_files_path")
def local_validate(
    mtbls_provisional_study_id: str,
    metadata_files_path: str,
    data_files_path: None | str = None,
    output_directory: None | str = None,
    overridden_rules_file_path: None | str = None,
    opa_executable_path: str = "opa",
    mtbls_validation_bundle_path: None | str = "./bundle.tar.gz",
    refetch_mtbls_validation_bundle: bool = False,
    mtbls_validation_bundle_url: str = "https://raw.githubusercontent.com/EBI-Metabolights/mtbls-validation/refs/heads/test/docs/bundle.tar.gz",
):
    """Validate local ISA metadata files."""
    if not data_files_path:
        data_files_path = Path(metadata_files_path) / Path("FILES")
    if not overridden_rules_file_path:
        overridden_rules = set()
        overridden_files = set()
    elif Path(overridden_rules_file_path).exists():
        overridden_rules = {
            x
            for x in Path(overridden_rules_file_path).read_text().split()
            if x and x.startswith("rule_")
        }
        overridden_files = {
            x
            for x in Path(overridden_rules_file_path).read_text().split()
            if x and len(x) > 2 and x[:2] in {"a_", "i_", "s_", "m_"}
        }
    if not output_directory:
        output_directory = ".mtbls-validation-outputs"
    Path(output_directory).mkdir(exist_ok=True, parents=True)
    mtbls_validation_input_file_path = (
        f"{output_directory}/{mtbls_provisional_study_id}_mtbls_validation_input.json"
    )

    mtbls_validation_result_file_path = (
        f"{output_directory}/{mtbls_provisional_study_id}_mtbls_validation_output.json"
    )
    mtbls_validation_errors_file_path = (
        f"{output_directory}/{mtbls_provisional_study_id}_mtbls_validation_errors.json"
    )
    if (
        refetch_mtbls_validation_bundle
        or not Path(mtbls_validation_bundle_path).exists()
    ):
        if not mtbls_validation_bundle_url:
            click.echo(
                f"Validation bundle does not exist on {mtbls_validation_bundle_path}"
            )
            return False
        else:
            download_file(mtbls_validation_bundle_url, mtbls_validation_bundle_path)

    provider = MetabolightsStudyProvider(
        db_metadata_collector=None,
        folder_metadata_collector=LocalFolderMetadataCollector(),
    )

    model: MetabolightsStudyModel = provider.load_study(
        mtbls_provisional_study_id,
        study_path=metadata_files_path,
        connection=None,
        load_assay_files=True,
        load_sample_file=True,
        load_maf_files=True,
        load_folder_metadata=True,
        calculate_data_folder_size=False,
        calculate_metadata_size=False,
        data_files_path=str(data_files_path),
        data_files_mapping_folder_name="FILES",
    )
    json_validation_input = model.model_dump(by_alias=True)

    with open(mtbls_validation_input_file_path, "w") as f:
        json.dump(json_validation_input, f, indent=2)

    if not opa_executable_path:
        opa_executable_path = "opa"

    task = None
    local_command = [
        opa_executable_path,
        "eval",
        "--data",
        mtbls_validation_bundle_path,
        "data.metabolights.validation.v2.report.complete_report",
        "-i",
        mtbls_validation_input_file_path,
    ]

    try:
        task = subprocess.run(
            local_command, capture_output=True, text=True, check=True, timeout=120
        )
        if task.returncode != 0:
            click.echo("Validation processes failed.")
            click.echo(task.stdout)
            click.echo(task.stderr)
            return False
        raw_validation_result = json.loads(task.stdout)
        validation_result = (
            raw_validation_result.get("result")[0].get("expressions")[0].get("value")
        )

        violation_results = OpaValidationResult.model_validate(validation_result)
        errors = [
            x
            for x in violation_results.violations
            if x.type == PolicyMessageType.ERROR
            and x.identifier not in overridden_rules
            and x.source_file not in overridden_files
        ]
        overridden_errors = {}
        overridden_files_map = {}
        for x in violation_results.violations:
            if x.type == PolicyMessageType.ERROR and x.identifier in overridden_rules:
                if x.identifier not in overridden_errors:
                    overridden_errors[x.identifier] = []
                overridden_errors[x.identifier].append(x)
                x.overridden = True
                x.override_comment = "rule id is in the exclude list"
                x.type = PolicyMessageType.WARNING
            elif (
                x.type == PolicyMessageType.ERROR and x.source_file in overridden_files
            ):
                if x.source_file not in overridden_files_map:
                    overridden_files_map[x.source_file] = []
                overridden_files_map[x.source_file].append(x.identifier)
                x.overridden = True
                x.override_comment = "file name is in the exclude list"
                x.type = PolicyMessageType.WARNING

        violation_results.summary = []

        with open(mtbls_validation_result_file_path, "w") as f:
            json.dump(violation_results.model_dump(by_alias=True), f, indent=2)

        # for idx, x in enumerate(errors):
        #     click.echo(f"{idx + 1}\t{x.identifier}\t{x.violation}")
        if errors:
            with open(mtbls_validation_errors_file_path, "w") as f:
                json.dump(
                    {"errors": [x.model_dump(by_alias=True) for x in errors]},
                    f,
                    indent=2,
                )

            click.echo(
                f"ERRORS\nNumber of errors: {len(errors)}. "
                f"Validation results and errors stored on "
                f"{mtbls_validation_result_file_path} and"
                f" {mtbls_validation_errors_file_path} respectively."
            )
        else:
            click.echo(
                "SUCCESS\n"
                f"Validation result is stored on {mtbls_validation_result_file_path}"
            )
        if overridden_errors:
            click.echo(
                f"Overridden rules: {', '.join([f'{k} ({len(v)})' for k, v in overridden_errors.items()])}"
            )
        if overridden_files_map:
            files = []
            for k, v in overridden_files_map.items():
                rules = ", ".join(v)
                files.append(f"{k} ({len(v)} - {rules})")
            click.echo(f"Overridden file rules: {', '.join(files)}")
        return True
    except subprocess.TimeoutExpired as exc:
        click.echo("The validation process timed out.")
        click.echo(exc.stderr)
        return False
    except subprocess.CalledProcessError as exc:
        click.echo("The validation process call failed.")
        click.echo(exc.stdout)
        click.echo(exc.stderr)
        return False
    except (OSError, subprocess.SubprocessError) as exc:
        click.echo("The validation failed.")
        if task and task.stderr:
            click.echo(task.stderr)
        else:
            click.echo(str(exc))
        return False


if __name__ == "__main__":
    local_validate(
        [
            "MTBLS1",
            "tests/test-data/MTBLS1",
            "--data_files_path",
            "tests/test-data/MTBLS1/FILES",
            "--output_directory",
            "outputs",
            "--overridden_rules_file_path",
            "mtbls_overriden_rules.txt",
        ]
    )
