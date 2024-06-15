import datetime
import json
import os
import time
from typing import List, Set, Tuple, Union

import httpx
from dateutil import parser
from pydantic import BaseModel

from metabolights_utils.commands.submission.model import (
    FtpLoginCredentials,
    LoginCredentials,
    RestApiCredentials,
    StudyResponse,
    SubmittedStudiesResponse,
)
from metabolights_utils.commands.submission.utils import (
    get_submission_private_ftp_credentials,
    get_submission_rest_api_credentials,
)
from metabolights_utils.common import sort_by_study_id
from metabolights_utils.models.common import ErrorMessage, GenericMessage, InfoMessage
from metabolights_utils.models.enums import GenericMessageType
from metabolights_utils.models.metabolights.model import (
    MetabolightsStudyModel,
    StudyFolderMetadata,
)
from metabolights_utils.provider import definitions
from metabolights_utils.provider.ftp.default_ftp_client import (
    DefaultFtpClient,
    LocalDirectory,
)
from metabolights_utils.provider.ftp.folder_metadata_collector import (
    FtpFolderMetadataCollector,
)
from metabolights_utils.provider.local_folder_metadata_collector import (
    LocalFolderMetadataCollector,
)
from metabolights_utils.provider.study_provider import (
    AbstractDbMetadataCollector,
    AbstractFolderMetadataCollector,
    MetabolightsStudyProvider,
)
from metabolights_utils.provider.submission_model import (
    ValidationMessage,
    ValidationReport,
    ValidationResponse,
)
from metabolights_utils.provider.utils import (
    download_file_from_rest_api,
    is_metadata_file,
    is_metadata_filename_pattern,
    rest_api_get,
)


class MetabolightsSubmissionRepository:
    def __init__(
        self,
        local_storage_root_path: Union[None, str] = None,
        credentials_file_path: Union[None, str] = None,
        ftp_server_url: Union[None, str] = None,
        rest_api_base_url: Union[None, str] = None,
        local_storage_cache_path: Union[None, str] = None,
    ) -> None:
        self.ftp_server_url = ftp_server_url
        if not self.ftp_server_url:
            self.ftp_server_url = definitions.default_private_ftp_server_url

        self.local_storage_cache_path = local_storage_cache_path
        if not local_storage_cache_path:
            self.local_storage_cache_path = (
                definitions.default_local_submission_cache_path
            )
        self.local_storage_root_path = local_storage_root_path
        if not self.local_storage_root_path:
            self.local_storage_root_path = (
                definitions.default_local_submission_root_path
            )

        self.credentials_file_path = credentials_file_path
        if not self.credentials_file_path:
            self.credentials_file_path = (
                definitions.default_local_submission_credentials_file_path
            )
        self.rest_api_base_url = rest_api_base_url
        if not self.rest_api_base_url:
            self.rest_api_base_url = definitions.default_rest_api_url

    def load_study_model(
        self,
        study_id: str,
        local_path: Union[str, None] = None,
        use_only_local_path: bool = False,
        override_local_files: bool = False,
        load_folder_metadata: bool = True,
        rebuild_folder_index_file: bool = False,
        folder_index_file_path: Union[str, None] = None,
        db_metadata_collector: Union[None, AbstractDbMetadataCollector] = None,
        folder_metadata_collector: Union[None, AbstractFolderMetadataCollector] = None,
    ) -> Tuple[Union[None, MetabolightsStudyModel], List[GenericMessage]]:
        if not study_id or not study_id.strip():
            return None, [ErrorMessage(short="Invalid study_id")]
        study_id = study_id.upper().strip("/")
        if not local_path:
            local_path = self.local_storage_root_path
        target_path = os.path.join(local_path, study_id)
        if not folder_index_file_path:
            folder_index_file_path = os.path.join(
                self.local_storage_cache_path,
                study_id,
                "mtbls_index.json",
            )

        model: Union[None, MetabolightsStudyModel] = None
        messages = []
        if use_only_local_path:
            provider = MetabolightsStudyProvider(
                db_metadata_collector=db_metadata_collector,
                folder_metadata_collector=folder_metadata_collector,
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

            return model, [InfoMessage(short="Loaded from local isa metadata files.")]

        messages: List[GenericMessage] = []
        try:
            result = self.download_submission_metadata_files(
                study_id=study_id,
                local_path=local_path,
                metadata_files=None,
                override_local_files=override_local_files,
                delete_unlisted_metadata_files=True,
            )
            if result.success:

                messages.append(
                    InfoMessage(
                        short=f"Downloaded metadata file with response",
                        detail=f"Response message: {result.code} {result.message}",
                    )
                )

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
                    calculate_data_folder_size=False,
                    calculate_metadata_size=False,
                )
            else:
                messages.append(
                    ErrorMessage(
                        short=f"Download metadata file failure.",
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
        return model, messages

    def upload_metadata_files(
        self,
        study_id,
        remote_folder_directory: Union[str, None] = None,
        local_path: Union[str, None] = None,
        credentials_file_path: Union[str, None] = None,
        ftp_server_url: Union[str, None] = None,
        metadata_files: Union[List[str], None] = None,
        override_remote_files: bool = False,
    ):
        if not local_path:
            local_path = self.local_storage_root_path
        if not credentials_file_path:
            credentials_file_path = self.credentials_file_path
        if not ftp_server_url:
            ftp_server_url = self.ftp_server_url

        response, errors = self.list_isa_metadata_files(study_id=study_id)
        if not response:
            return False, "Errors while listing metadata files."
        if not remote_folder_directory and response.upload_path:
            remote_folder_directory = response.upload_path
        modified_time_dict = {}
        new_requested_files = []
        for descriptor in response.study:
            _time = descriptor.created_at
            modified = parser.parse(_time).timestamp()
            remote_modified_time = int(modified)
            modified_time_dict[descriptor.file] = remote_modified_time
        study_path = os.path.join(self.local_storage_root_path, study_id)
        if not metadata_files or override_remote_files:
            files = os.listdir(study_path)
            metadata_files = [x for x in files if is_metadata_filename_pattern(x)]
        if override_remote_files:
            new_requested_files = metadata_files
        else:
            for file_name in metadata_files:
                relative_path = file_name.removeprefix(f"{local_path}/")
                remote_modified_time = None
                if relative_path in modified_time_dict:
                    remote_modified_time = modified_time_dict[relative_path]
                file_path = os.path.join(study_path, file_name)
                if remote_modified_time:
                    local_modified_time = int(os.path.getmtime(file_path))
                    if remote_modified_time > local_modified_time:
                        new_requested_files.append(relative_path)
                else:
                    new_requested_files.append(relative_path)
        if not new_requested_files and override_remote_files:
            return False, "No files to upload"
        username, password, error = self.get_ftp_credentials()
        if not error:
            ftp_client = DefaultFtpClient(
                local_storage_root_path=local_path,
                ftp_server_url=ftp_server_url,
                remote_repository_root_directory="",
                username=username,
                password=password,
            )
            input_files = [os.path.join(study_path, x) for x in new_requested_files]
            try:
                ftp_client.upload_files(remote_folder_directory, input_files)

                return True, None
            except Exception as ex:
                return False, str(ex)
        else:
            return False, error

    def check_api_response(self, api_name, response):
        if not response:
            return False, f"No response for {api_name}"
        code = response.status_code
        text = response.text
        if response.status_code in (200, 201):
            return True, None
        else:
            return (
                False,
                f"Failure of {api_name} {code}: {text}",
            )

    def validate_study(
        self,
        study_id,
        validation_file_path: Union[str, None] = None,
        pool_period: int = 5,
        retry: int = 20,
        timeout: int = 10,
    ):
        sub_path = f"/studies/{study_id}/validation-task"

        api_header, error = self.get_api_token()
        headers = {}
        if api_header:
            headers["User-Token"] = api_header
        else:
            return None, error

        api_name = "validation task start"
        try:
            url = os.path.join(self.rest_api_base_url.rstrip("/"), sub_path.lstrip("/"))
            parameters = {}
            response = httpx.post(
                url=url,
                timeout=timeout,
                headers=headers,
                params=parameters,
            )
            success, error = self.check_api_response(api_name, response)
            if not success:
                return None, error

            data = json.loads(response.text)
            task_start_response = ValidationResponse.model_validate(
                data, from_attributes=True
            )

            if not task_start_response.task.task_id:
                return (None, f"Failure of {api_name} for {study_id}.")

        except Exception as ex:
            return None, f"Validation task start failure: {str(ex)}."

        api_name = "validation task status check"
        try:
            task_success = False
            for i in range(retry + 1):
                time.sleep(pool_period)
                try:
                    response = httpx.get(
                        url=url,
                        timeout=timeout,
                        headers=headers,
                        params=parameters,
                    )
                except TimeoutError:
                    continue
                success, error = self.check_api_response(api_name, response)
                if not success:
                    continue
                data = json.loads(response.text)
                task_status_response = ValidationResponse.model_validate(
                    data, from_attributes=True
                )

                task = task_status_response.task
                status = task.last_status
                if task.task_id and task.last_status:
                    if "SUCCESS" in status.upper():
                        task_success = True
                        break
            if not task_success:
                return (None, f"Failure of {api_name} for {study_id}.")
        except Exception as ex:
            return None, f"{api_name} failure: {str(ex)}."

        api_name = "get validation report"
        try:
            api_success = False
            report_sub_path = f"/studies/{study_id}/validation-report"
            report_url = os.path.join(
                self.rest_api_base_url.rstrip("/"),
                report_sub_path.lstrip("/"),
            )
            for i in range(retry + 1):
                try:
                    response = httpx.get(
                        url=report_url,
                        timeout=timeout,
                        headers=headers,
                        params=parameters,
                    )
                except TimeoutError:
                    time.sleep(pool_period)
                    continue
                success, error = self.check_api_response(api_name, response)
                if not success:
                    time.sleep(pool_period)
                    continue
                data = json.loads(response.text)
                report = ValidationReport.model_validate(data, from_attributes=True)
                if report.validation.status:
                    api_success = True
                    break
            if not api_success:
                return (None, f"Failure of {api_name} for {study_id}.")
        except Exception as ex:
            return None, f"{api_name} failure: {str(ex)}."

        errors: List[ValidationMessage] = []
        for section in report.validation.validations:
            for message in section.details:
                if message.status.upper() == "ERROR":
                    errors.append(message)

        with open(validation_file_path, "w") as f:
            f.write(
                f"section\t"
                f"status\t"
                f"message\t"
                f"description\t"
                f"metadata_file\n"
            )
            for e in errors:
                f.write(
                    f"{e.section}\t"
                    f"{e.status}\t"
                    f"{e.message}\t"
                    f"{e.description}\t"
                    f"{e.metadata_file}\n"
                )
        return True, status

    def sync_private_ftp_metadata_files(
        self, study_id: str, pool_period: int = 10, retry: int = 10, timeout: int = 10
    ):
        sub_path = f"/studies/{study_id}/study-folders/rsync-task"
        api_header, error = self.get_api_token()
        headers = {}
        if api_header:
            headers["User-Token"] = api_header
        else:
            return None, error
        headers["Dry-Run"] = "false"
        headers["Sync-Type"] = "metadata"
        headers["Source-Staging-Area"] = "private-ftp"
        headers["Target-Staging-Area"] = "rw-study"

        url = os.path.join(self.rest_api_base_url.rstrip("/"), sub_path.lstrip("/"))
        parameters = {}
        response = httpx.post(
            url=url,
            timeout=timeout,
            headers=headers,
            params=parameters,
        )
        task_id = None
        if response and response.status_code in (200, 201):
            data = json.loads(response.text)
            if "task_id" in data:
                task_id = data["task_id"]

            if task_id:
                for i in range(retry + 1):
                    time.sleep(pool_period)
                    response = httpx.get(
                        url=url,
                        timeout=timeout,
                        headers=headers,
                        params=parameters,
                    )
                    if response:
                        data = json.loads(response.text)
                        if "status" in data:
                            status = data["status"]
                            if "SUCCESS" in status:
                                return True, status
                            elif "FAIL" in status:
                                return False, status
        else:
            return False, response.status_code if response else None

    def create_assay(
        self,
        study_id: str,
        assay_technique: str,
        scan_polarity: str = "",
        column_type: str = "",
        timeout: int = 10,
    ):
        api_header, error = self.get_api_token()
        headers = {}
        if api_header:
            headers["User-Token"] = api_header
        else:
            return None, None, error

        sub_path = f"/studies/{study_id}/assays"
        url = os.path.join(self.rest_api_base_url.rstrip("/"), sub_path.lstrip("/"))
        body = {"assay": {"type": assay_technique, "columns": []}}
        if scan_polarity:
            body["assay"]["columns"].append(
                {"name": "polarity", "value": scan_polarity.lower()}
            )
        if column_type:
            body["assay"]["columns"].append(
                {"name": "column type", "value": column_type.lower()}
            )

        response = httpx.post(
            url=url, timeout=timeout, headers=headers, params={}, json=body
        )
        if response and response.status_code in (200, 201):
            data = json.loads(response.text)
            if "filename" in data and "maf" in data:
                return data["filename"], data["maf"], None

            return None, None, "Invalid response."
        else:
            return None, None, response.status_code if response else None

    def download_submission_metadata_files(
        self,
        study_id: str,
        local_path: Union[str, None] = None,
        metadata_files: Union[List[str], None] = None,
        override_local_files: bool = False,
        delete_unlisted_metadata_files: bool = True,
    ) -> LocalDirectory:

        api_header, error = self.get_api_token()
        headers = {}
        if api_header:
            headers["User-Token"] = api_header
        else:
            return LocalDirectory(code=400, message=f"user token error: {error}")

        if not study_id:
            return LocalDirectory(code=400, message=f"Invalid study_id")
        if not local_path:
            local_path = self.local_storage_root_path
        response = LocalDirectory(root_path=local_path)

        study_id = study_id.upper().strip("/")

        listed_files = []
        requested_files = metadata_files
        if not metadata_files:
            result, error = self.list_isa_metadata_files(study_id)
            if result:
                file_names = [x.file for x in result.study]
                descriptors = {x.file: x for x in result.study}
                listed_files = set(file_names)
                requested_files = file_names
            else:
                return None, error

        if requested_files != metadata_files:
            filtered_files = [
                x for x in requested_files if is_metadata_filename_pattern(x)
            ]
            requested_files = filtered_files
        response.actions = {f"{study_id}/{x}": "SKIPPED" for x in requested_files}

        new_requested_files = []
        for filename in requested_files:
            file_path = os.path.join(local_path, study_id, filename)
            key = f"{study_id}/{filename}"
            if os.path.exists(file_path):
                if override_local_files:
                    response.actions[key] = "OVERRIDED"
                else:
                    local_modified_time = int(os.path.getmtime(file_path))
                    _time = descriptors[filename].created_at
                    modified = parser.parse(_time).timestamp()
                    remote_modified_time = int(modified)
                    if remote_modified_time > local_modified_time:
                        new_requested_files.append(filename)
                    else:
                        response.actions[key] = "SKIPPED"
            else:
                new_requested_files.append(filename)
                response.actions[key] = "DOWNLOADED"
        requested_files = new_requested_files

        if requested_files and not os.path.exists(local_path):
            os.makedirs(local_path, exist_ok=True)

        messages: List[GenericMessage] = []
        current_file = None
        try:
            sub_path = f"/studies/{study_id}/download"

            if not metadata_files:
                parameters = {"file": "metadata"}
            else:
                parameters["file"] = [",".join(metadata_files)]

            for filename in requested_files:
                new_file_path = os.path.join(local_path, study_id, filename)
                current_file = filename
                url = self.rest_api_base_url.strip("/") + "/" + sub_path.strip("/")
                _time = descriptors[filename].created_at
                modified = parser.parse(_time).timestamp()
                remote_modified_time = int(modified)
                download_file_from_rest_api(
                    url,
                    new_file_path,
                    timeout=60,
                    headers=headers,
                    parameters=parameters,
                    modification_time=remote_modified_time,
                    is_zip_response=True,
                )

            if delete_unlisted_metadata_files:
                for filename in os.listdir(local_path):
                    if filename not in listed_files:
                        file_path = os.path.join(local_path, filename)
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
                    detail=f"Error message: {str(ex)}",
                )
            )

        return response

    def list_isa_metadata_files(
        self, study_id: str
    ) -> Tuple[Union[StudyResponse, None], Union[None, str]]:

        response, error = self.list_study_directory(study_id=study_id)
        if response:
            response.study = [
                x for x in response.study if is_metadata_filename_pattern(x.file)
            ]
            return response, None
        else:
            response, error

    def list_studies(
        self, timeout=None, headers=None, parameters=None
    ) -> Tuple[Union[None, SubmittedStudiesResponse], Union[str, None]]:
        api_header, error = self.get_api_token()
        headers = {}
        if api_header:
            headers["User-Token"] = api_header
        else:
            return None, error

        sub_path = "/studies/user"
        url = os.path.join(self.rest_api_base_url.rstrip("/"), sub_path.lstrip("/"))
        response = httpx.get(
            url=url,
            timeout=timeout,
            headers=headers,
            params=parameters,
        )
        if response and response.status_code in (200, 201):
            data = json.loads(response.text)
            studies_data = SubmittedStudiesResponse.model_validate(data)
            studies = studies_data.data.copy()
            studies.sort(key=lambda x: x.updated)

            return studies_data, None
        else:
            return studies_data, response.status_code if response else None

    def get_api_token(self):
        result = None
        if self.credentials_file_path:
            credentials: RestApiCredentials = get_submission_rest_api_credentials(
                credentials_file_path=self.credentials_file_path,
                rest_api_base_url=self.rest_api_base_url,
            )
            result = credentials.api_token if credentials else None

        if not result:
            return (
                None,
                f"There is not user api token for {self.rest_api_base_url} "
                "Rest API. Login before to use the command.",
            )
        return (result, None)

    def get_ftp_credentials(self):
        result = None
        if self.credentials_file_path:
            credentials: FtpLoginCredentials = get_submission_private_ftp_credentials(
                credentials_file_path=self.credentials_file_path,
                private_ftp_url=self.ftp_server_url,
            )
            result = credentials if credentials else None

        if not result:
            return (
                None,
                None,
                f"There is not user api token for {self.rest_api_base_url} "
                "Rest API. Login before to use the command.",
            )
        return (result.user_name, result.password, None)

    def list_study_directory(
        self, study_id: str, subdirectory: Union[str, None] = None, timeout=None
    ) -> Tuple[Union[None, StudyResponse], Union[None, str]]:
        study_id = study_id.upper().strip("/") if study_id else ""
        api_header, error = self.get_api_token()
        headers = {}
        if api_header:
            headers["User-Token"] = api_header
        else:
            return None, error

        sub_path = f"/studies/{study_id}/files/tree"
        parameters = {
            "location": "study",
            "include_sub_dir": False,
            "include_internal_files": False,
        }
        paths = [study_id.strip("/")]
        if subdirectory:
            parameters["directory"] = subdirectory.lstrip("/")
            paths.append(subdirectory.strip("/"))
        url = os.path.join(self.rest_api_base_url.rstrip("/"), sub_path.lstrip("/"))
        data, error = rest_api_get(
            url, timeout=timeout, parameters=parameters, headers=headers
        )
        if data:
            studies_response = StudyResponse.model_validate(data)
            studies_response.study.sort(key=lambda x: x.file)
            return studies_response, None
        else:
            return None, error

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
