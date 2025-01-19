import json
import logging
import os
from typing import List, Set, Tuple, Union

from metabolights_utils.common import sort_by_study_id
from metabolights_utils.models.common import (
    ErrorMessage,
    GenericMessage,
    InfoMessage,
    WarningMessage,
)
from metabolights_utils.models.enums import GenericMessageType
from metabolights_utils.models.metabolights.model import (
    MetabolightsStudyModel,
    StudyFolderMetadata,
)
from metabolights_utils.provider import definitions
from metabolights_utils.provider.ftp.default_ftp_client import (
    DefaultFtpClient,
    FtpFolderContent,
    LocalDirectory,
)
from metabolights_utils.provider.ftp.folder_metadata_collector import (
    FtpFolderMetadataCollector,
)
from metabolights_utils.provider.ftp.model import FtpFiles
from metabolights_utils.provider.local_folder_metadata_collector import (
    LocalFolderMetadataCollector,
)
from metabolights_utils.provider.study_provider import (
    AbstractDbMetadataCollector,
    MetabolightsStudyProvider,
)
from metabolights_utils.provider.utils import (
    is_metadata_file,
    is_metadata_filename_pattern,
)
from metabolights_utils.utils.filename_utils import join_path

logger = logging.getLogger(__name__)


class MetabolightsFtpRepository(DefaultFtpClient):
    def __init__(
        self,
        local_storage_root_path: Union[None, str] = None,
        ftp_server_url: Union[None, str] = None,
        remote_repository_root_directory: Union[None, str] = None,
        local_storage_cache_path: Union[None, str] = None,
    ) -> None:
        self.local_storage_cache_path = local_storage_cache_path
        if not local_storage_cache_path:
            self.local_storage_cache_path = (
                definitions.default_local_repority_cache_path
            )
        self.local_storage_cache_path = join_path(self.local_storage_cache_path)
        logger.debug(
            "local_storage_cache_path is set to path: %s",
            self.local_storage_cache_path,
        )
        self.local_storage_root_path = local_storage_root_path
        if not self.local_storage_root_path:
            self.local_storage_root_path = (
                definitions.default_local_repository_root_path
            )
        self.local_storage_root_path = join_path(self.local_storage_root_path)
        logger.debug(
            "local_storage_root_path is set to path: %s",
            self.local_storage_root_path,
        )
        self.ftp_server_url = ftp_server_url
        if not self.ftp_server_url:
            self.ftp_server_url = definitions.default_ftp_server_url
        logger.debug(
            "ftp_server_url is set to URL: %s",
            self.ftp_server_url,
        )
        self.remote_repository_root_directory = remote_repository_root_directory
        if not self.remote_repository_root_directory:
            self.remote_repository_root_directory = (
                definitions.default_remote_repository_root_directory
            )
        self.remote_repository_root_directory = (
            self.remote_repository_root_directory.replace("\\", "/")
        )
        logger.debug(
            "remote_repository_root_directory is set to directory: %s",
            self.remote_repository_root_directory,
        )
        self.ftp_client = DefaultFtpClient(
            local_storage_root_path=self.local_storage_root_path,
            ftp_server_url=self.ftp_server_url,
            remote_repository_root_directory=self.remote_repository_root_directory,
        )

    def load_study_model(
        self,
        study_id: str,
        local_path: Union[str, None] = None,
        use_only_local_path: bool = False,
        override_local_files: bool = False,
        load_folder_metadata: bool = True,
        rebuild_folder_index_file: bool = False,
        folder_index_file_path: Union[str, None] = None,
        use_study_model_cache: Union[bool, None] = True,
        study_model_file_path: Union[str, None] = None,
        db_metadata_collector: Union[None, AbstractDbMetadataCollector] = None,
    ) -> Tuple[Union[None, MetabolightsStudyModel], List[GenericMessage]]:
        if not study_id or not study_id.strip():
            return None, [ErrorMessage(short="Invalid study_id")]
        study_id = study_id.upper().strip("/")
        if not local_path:
            local_path = self.local_storage_root_path

        target_path = join_path(local_path, study_id)
        if not folder_index_file_path:
            folder_index_file_path = join_path(
                self.local_storage_cache_path,
                study_id,
                "mtbls_index.json",
            )
        model_cache_path = study_model_file_path
        if not study_model_file_path:
            model_cache_path = join_path(
                self.local_storage_cache_path,
                study_id,
                "study_model.json",
            )

        model: Union[None, MetabolightsStudyModel] = None
        messages = []
        if use_study_model_cache:
            try:
                if os.path.exists(model_cache_path):
                    with open(model_cache_path, encoding="utf-8") as f:
                        data = json.load(f)
                        model = MetabolightsStudyModel.model_validate(data)
                        if model.investigation_file_path == "i_Investigation.txt":
                            messages.append(
                                InfoMessage(short="Loaded from cache file.")
                            )
                            return model, messages
                        else:
                            messages.append(
                                WarningMessage(
                                    short="Cache file is not valid. Skipping..."
                                )
                            )
                else:
                    messages.append(
                        InfoMessage(short="There is no study model cache file.")
                    )
            except Exception as ex:
                messages.append(
                    WarningMessage(
                        short=f"Study model cache file load error: {str(ex)}."
                    )
                )
        if use_only_local_path:
            provider = MetabolightsStudyProvider(
                db_metadata_collector=db_metadata_collector,
                folder_metadata_collector=LocalFolderMetadataCollector(),
            )
            model: MetabolightsStudyModel = provider.load_study(
                study_id,
                study_path=target_path,
                connection=None,
                load_assay_files=True,
                load_sample_file=True,
                load_maf_files=True,
                load_folder_metadata=load_folder_metadata,
                calculate_data_folder_size=True,
                calculate_metadata_size=True,
            )
            if model:
                parent = os.path.dirname(model_cache_path)
                os.makedirs(parent, exist_ok=True)
                with open(model_cache_path, "w", encoding="utf-8") as fw:
                    fw.write(model.model_dump_json(indent=4))

            return model, [InfoMessage(short="Loaded from local isa metadata files.")]

        messages: List[GenericMessage] = []
        try:
            result = self.download_study_metadata_files(
                study_id=study_id,
                local_path=local_path,
                metadata_files=None,
                override_local_files=override_local_files,
                delete_unlisted_metadata_files=True,
            )
            if result.success:
                messages.append(
                    InfoMessage(
                        short="Downloaded metadata file with response",
                        detail=f"Response message: {result.code} {result.message}",
                    )
                )

                provider = MetabolightsStudyProvider(
                    db_metadata_collector=db_metadata_collector,
                    folder_metadata_collector=FtpFolderMetadataCollector(
                        client=self.ftp_client,
                        study_id=study_id,
                        folder_index_file_path=folder_index_file_path,
                        rebuild_folder_index_file=rebuild_folder_index_file,
                    ),
                )
                model: MetabolightsStudyModel = provider.load_study(
                    study_id,
                    study_path=target_path,
                    connection=None,
                    load_assay_files=True,
                    load_sample_file=True,
                    load_maf_files=True,
                    load_folder_metadata=load_folder_metadata,
                    calculate_data_folder_size=False,
                    calculate_metadata_size=False,
                )
            else:
                messages.append(
                    ErrorMessage(
                        short="Download metadata file failure.",
                        detail=f"Error message: {result.code} {result.message}",
                    )
                )

        except Exception as ex:
            messages.append(
                ErrorMessage(
                    short="Download metadata file failure. Try -l option if there is a local copy.",
                    detail=str(ex),
                )
            )
        if model:
            parent = os.path.dirname(model_cache_path)
            os.makedirs(parent, exist_ok=True)
            with open(model_cache_path, "w", encoding="utf-8") as fw:
                fw.write(model.model_dump_json(indent=4))
        return model, messages

    def download_study_metadata_files(
        self,
        study_id: str,
        local_path: Union[List[str], None] = None,
        metadata_files: Union[List[str], None] = None,
        override_local_files: bool = False,
        delete_unlisted_metadata_files: bool = True,
    ) -> LocalDirectory:
        if not study_id:
            return LocalDirectory(root_path="", code=400, message="invalid study_id")
        if not local_path:
            local_path = f"{self.local_storage_root_path}/{study_id}"
        local_path = join_path(local_path)
        response = LocalDirectory(root_path=local_path)

        study_id = study_id.upper().strip("/")

        listed_files = []
        requested_files = metadata_files
        if not metadata_files:
            result = self.list_isa_metadata_files(study_id)
            if result and result.success:
                listed_files = set(result.files)
                requested_files = result.files
            else:
                return LocalDirectory(
                    success=False,
                    code=result.code,
                    message=result.message,
                    local_files=result.files,
                    root_path=local_path,
                )
        if requested_files != metadata_files:
            filtered_files = [
                x for x in requested_files if is_metadata_filename_pattern(x)
            ]
            requested_files = filtered_files
        if requested_files and not os.path.exists(local_path):
            os.makedirs(local_path, exist_ok=True)

        response.actions = {f"{study_id}/{x}": "SKIPPED" for x in listed_files}
        messages: List[GenericMessage] = []
        current_file = None
        try:
            for filename in requested_files:
                # new_local_path = os.path.join(local_path, study_id)
                new_relative_file_path = f"{study_id}/{filename}".replace(
                    "\\", "/"
                ).rstrip("/")
                current_file = filename
                self.ftp_client.download_file(
                    relative_file_path=new_relative_file_path,
                    local_path=local_path,
                    local_files=response,
                    override_local_files=override_local_files,
                    skip_files=None,
                    delete_unlisted_local_files=False,
                    keep_local_files=True,
                )
            if delete_unlisted_metadata_files:
                for filename in os.listdir(local_path):
                    if filename not in listed_files:
                        file_path = join_path(local_path, filename)
                        if is_metadata_file(file_path):
                            response.actions[filename] = "DELETED"
                            os.remove(file_path)
            response.success = True
            response.code = 200
            response.message = "Ok"

        except Exception as ex:
            messages.append(
                ErrorMessage(
                    short=f"Download data file {current_file if current_file else ''} failure",
                    detail=f"Error message: {result.message}, {str(ex)}",
                )
            )

        return response

    def download_study_data_files(
        self,
        study_id: str,
        selected_data_files: Union[List[str], None] = None,
        local_path: Union[List[str], None] = None,
        override_local_files: bool = False,
        skip_files: Union[Set[str], None] = None,
        delete_unlisted_local_files: bool = False,
        keep_local_files: Union[Set[str], None] = None,
    ) -> LocalDirectory:
        if not study_id or not study_id.strip():
            return LocalDirectory(
                code=400,
                message="Invalid study_id",
                root_path=local_path,
            )
        if not local_path:
            local_path = f"{self.local_storage_root_path}/{study_id}"

        response = LocalDirectory(root_path=local_path)
        if not selected_data_files:
            selected_data_files = ["FILES"]
        study_id = study_id.upper().strip("/")
        try:
            for file in selected_data_files:
                new_relative_file_path = f"{study_id}/{file}".replace("\\", "/").rstrip(
                    "/"
                )
                self.ftp_client.download_file(
                    relative_file_path=new_relative_file_path,
                    local_path=local_path,
                    local_files=response,
                    override_local_files=override_local_files,
                    skip_files=skip_files,
                    delete_unlisted_local_files=delete_unlisted_local_files,
                    keep_local_files=keep_local_files,
                )
            response.success = True
            response.code = 200
            response.message = "Ok"
        except Exception as ex:
            response.code = 500
            response.message = str(ex)

        return response

    def list_isa_metadata_files(self, study_id: str) -> FtpFiles:
        response: FtpFolderContent = self.list_study_directory(study_id=study_id)
        isa_files = FtpFiles.model_validate(response.model_dump(), from_attributes=True)
        if response and response.success:
            isa_files.files = []
            for file in response.files:
                if is_metadata_filename_pattern(file):
                    isa_files.files.append(file)
        return isa_files

    def list_studies(self) -> Tuple[List[str], List[GenericMessage]]:
        try:
            result = self.ftp_client.list_directory(None)
            if result.success and result.folders:
                folders = [
                    x.base_name
                    for x in result.descriptors
                    if x.is_directory and x.base_name.startswith("MTBLS")
                ]
                folders.sort(key=sort_by_study_id)
                return folders, []
            else:
                return None, ErrorMessage(
                    short="List study folder failure",
                    detail=f"Response {result.code} {result.message}",
                )
        except Exception as ex:
            return None, ErrorMessage(short="List study folder failure", detail=str(ex))

    def list_study_directory(
        self, study_id: str, subdirectory: Union[str, None] = None
    ) -> FtpFolderContent:
        study_id = study_id.upper().strip("/") if study_id else ""

        directory = f"{study_id}/{subdirectory}" if subdirectory else study_id
        return self.ftp_client.list_directory(directory)

    def rebuild_study_folder_content(
        self, study_id: str, folder_index_file_path: Union[str, None] = None
    ) -> Tuple[Union[None, StudyFolderMetadata], List[GenericMessage]]:
        return self.get_study_folder_content(
            study_id=study_id,
            folder_index_file_path=folder_index_file_path,
            rebuild_folder_index_file=True,
        )

    def get_study_folder_content(
        self,
        study_id: str,
        folder_index_file_path: Union[str, None] = None,
        rebuild_folder_index_file: bool = False,
    ) -> Tuple[Union[None, StudyFolderMetadata], List[GenericMessage]]:
        if not study_id:
            return None, [
                GenericMessage(type=GenericMessageType.ERROR, short="Invalid study_id")
            ]

        study_id = study_id.upper().strip("/")

        collector = FtpFolderMetadataCollector(
            client=self.ftp_client,
            study_id=study_id,
            folder_index_file_path=folder_index_file_path,
            rebuild_folder_index_file=rebuild_folder_index_file,
        )

        metadata, messages = collector.get_folder_metadata(study_path=None)

        return metadata, messages
