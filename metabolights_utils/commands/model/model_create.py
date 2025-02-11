import json

import click

from metabolights_utils.models.metabolights.model import (
    MetabolightsStudyModel,
)
from metabolights_utils.provider.local_folder_metadata_collector import (
    LocalFolderMetadataCollector,
)
from metabolights_utils.provider.study_provider import (
    MetabolightsStudyProvider,
)


@click.command(no_args_is_help=True, name="create")
@click.option(
    "--output_path",
    "-o",
    help="output file path. e.g. /path/to/output.json",
)
@click.argument("study_path")
def model_create(
    study_path: str,
    output_path: str = "",
):
    """
    Validate submitted study and save validation report on local storage.
    NOTE: Data files should be on FILES subfolder.

    study_path: MetaboLights study folder. Folder should contain ISAtab files.

    output: Output JSON file path. If it is not defined, file is created on working directory.

    """
    folder_metadata_collector = LocalFolderMetadataCollector()
    provider = MetabolightsStudyProvider(
        folder_metadata_collector=folder_metadata_collector,
    )
    model: MetabolightsStudyModel = provider.load_study(
        "temp_study_id",
        study_path=study_path,
        connection=None,
        load_assay_files=True,
        load_sample_file=True,
        load_maf_files=True,
        load_folder_metadata=True,
        calculate_data_folder_size=True,
        calculate_metadata_size=True,
    )
    if not output_path and model.investigation.studies:
        output_path = f"./{model.investigation.studies[0].identifier}.json"

    if model.parser_messages:
        for file, messages in model.parser_messages.items():
            if messages:
                click.echo(f"Messages for {file}")
                for message in messages:
                    click.echo("-", message.type, message.short, message.detail)
    json.dump(model.model_dump(by_alias=True), open(output_path, "w"), indent=2)


if __name__ == "__main__":
    model_create(["tests/test-data/MTBLS1", "-o", "./test-outputs/MTBLS1.json"])
