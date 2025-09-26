import datetime
import io
import json
import os
import time
from pathlib import Path
from typing import List, Literal, Tuple, Union

import httpx

from metabolights_utils.commands.submission.model import (
    FtpLoginCredentials,
    RestApiCredentials,
    StudyResponse,
    SubmittedStudiesResponse,
)
from metabolights_utils.commands.submission.utils import (
    get_submission_private_ftp_credentials,
    get_submission_rest_api_credentials,
)
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
    APIResponse,
    FtpUploadDetails,
    PolicyResultResponse,
    ValidationMessage,
    ValidationReport,
    ValidationResponse,
    WorkerTaskStatus,
)
from metabolights_utils.provider.utils import (
    download_file_from_rest_api,
    is_metadata_file,
    is_metadata_filename_pattern,
    rest_api_get,
)
from metabolights_utils.utils.filename_utils import join_path


class MetabolightsSubmissionRepository:
    def __init__(
        self,
        local_storage_root_path: Union[None, str] = None,
        credentials_file_path: Union[None, str] = None,
        ftp_server_url: Union[None, str] = None,
        rest_api_base_url: Union[None, str] = None,
        validation_api_base_url: Union[None, str] = None,
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
        self.validation_api_base_url = validation_api_base_url
        if not self.validation_api_base_url:
            self.validation_api_base_url = definitions.default_validation_api_url

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
                        short="Downloaded metadata file with response",
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
                        short="Download metadata file failure.",
                        detail=f"Error message: {result.code} {result.message}",
                    )
                )

        except Exception as ex:
            messages.append(
                ErrorMessage(
                    short="Download metadata file failure. "
                    "Try -l option if there is a local copy.",
                    detail=str(ex),
                )
            )
        return model, messages

    def upload_metadata_files(
        self,
        study_id,
        remote_folder_directory: Union[str, None] = None,
        local_path: Union[str, None] = None,
        ftp_server_url: Union[str, None] = None,
        metadata_files: Union[List[str], None] = None,
        override_remote_files: bool = False,
        ftp_username: Union[str, None] = None,
        ftp_password: Union[str, None] = None,
        user_api_token: Union[str, None] = None,
    ) -> Tuple[bool, str]:
        if not local_path:
            local_path = self.local_storage_root_path
        local_path = join_path(local_path)

        if not ftp_server_url:
            ftp_server_url = self.ftp_server_url

        response, errors = self.list_isa_metadata_files(
            study_id=study_id, user_api_token=user_api_token
        )
        if not response:
            return False, "Errors while listing metadata files."
        if not remote_folder_directory:
            if response.upload_path:
                remote_folder_directory = response.upload_path
            else:
                return False, "Remote folder does not defined."
        modified_time_dict = {}
        new_requested_files = []
        for descriptor in response.study:
            _time = descriptor.created_at
            try:
                modified = datetime.datetime.strptime(  # noqa: DTZ007
                    _time, "%Y-%m-%d %H:%M:%S"
                ).timestamp()
            except ValueError:
                modified = 0
            remote_modified_time = int(modified)
            modified_time_dict[descriptor.file] = remote_modified_time
        study_folder = Path(local_path) / Path(study_id)
        study_path = str(study_folder.resolve())
        if not study_folder.exists():
            return False, f"Study path does not exist: {study_path}"
        if not metadata_files or override_remote_files:
            files = os.listdir(study_path)
            metadata_files = [x for x in files if is_metadata_filename_pattern(x)]
        if override_remote_files:
            new_requested_files = metadata_files
        else:
            for file_name in metadata_files:
                relative_path = file_name.replace(f"{local_path}/", "", 1)
                remote_modified_time = None
                if relative_path in modified_time_dict:
                    remote_modified_time = modified_time_dict[relative_path]
                file_path = study_folder / Path(file_name)
                if remote_modified_time:
                    local_modified_time = int(file_path.stat().st_mtime)
                    if remote_modified_time < local_modified_time:
                        new_requested_files.append(relative_path)
                else:
                    new_requested_files.append(relative_path)
        if not new_requested_files:
            return (
                False,
                "There is no metadata file to upload or "
                "local metadata files are up-to-date.",
            )
        if not ftp_password or not ftp_username:
            ftp_username, ftp_password, error = self.get_ftp_credentials()

        ftp_client = DefaultFtpClient(
            local_storage_root_path=local_path,
            ftp_server_url=ftp_server_url,
            remote_repository_root_directory="",
            username=ftp_username,
            password=ftp_password,
        )
        input_files = [str(study_folder / Path(x)) for x in new_requested_files]
        try:
            success, message = ftp_client.upload_files(
                remote_folder_directory, input_files
            )
            if success:
                return success, "Uploaded Files: " + ", ".join(new_requested_files)
            else:
                return success, message
        except Exception as ex:
            return False, str(ex)

    def upload_data_files(
        self,
        study_id,
        local_path: Union[str, None] = None,
        remote_folder_directory: Union[str, None] = None,
        ftp_server_url: Union[str, None] = None,
        ftp_username: Union[str, None] = None,
        ftp_password: Union[str, None] = None,
    ) -> Tuple[bool, str]:
        if not local_path:
            local_path = self.local_storage_root_path
        local_study_path = join_path(local_path, study_id)
        if not ftp_server_url:
            ftp_server_url = self.ftp_server_url
        study_folder = Path(local_study_path)
        study_path = str(study_folder.resolve())
        if not study_folder.exists():
            return False, f"Study path does not exist: {study_path}"

        files = study_folder.rglob("*")

        input_files = [
            x for x in files if not is_metadata_filename_pattern(Path(x).name)
        ]

        # username, password, error = self.get_ftp_credentials()
        ftp_client = DefaultFtpClient(
            local_storage_root_path=local_path,
            ftp_server_url=ftp_server_url,
            remote_repository_root_directory="",
            username=ftp_username,
            password=ftp_password,
        )
        try:
            ftp_client.upload_files(remote_folder_directory, input_files)
            return True, "Uploaded Files: " + ", ".join(input_files)
        except Exception as ex:
            return False, str(ex)

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

    def get_ftp_upload_details(
        self,
        study_id,
        rest_api_base_url: Union[str, None] = None,
        user_api_token: Union[str, None] = None,
        timeout: int = 5,
    ) -> Tuple[Union[None, FtpUploadDetails], str]:
        headers = {}
        if not user_api_token:
            user_api_token, error = self.get_api_token()
            if not user_api_token:
                return None, error
        sub_path = f"/studies/{study_id}/upload-info"
        headers["User-Token"] = user_api_token

        api_name = "get private ftp upload details"
        rest_api_base_url = (
            rest_api_base_url if rest_api_base_url else self.rest_api_base_url
        )
        try:
            url = f"{rest_api_base_url.rstrip('/')}/{sub_path.lstrip('/')}"
            parameters = {}
            response = httpx.get(
                url=url,
                timeout=timeout,
                headers=headers,
                params=parameters,
            )
            success, error = self.check_api_response(api_name, response)
            if not success:
                return None, error

            data = json.loads(response.text)
            details = FtpUploadDetails.model_validate(data, from_attributes=True)
            return details, ""
        except Exception as ex:
            return None, f"Validation task start failure: {str(ex)}."

    def validate_study(
        self,
        study_id,
        validation_file_path: Union[str, None] = None,
        pool_period: int = 5,
        retry: int = 20,
        timeout: int = 10,
    ):
        if not validation_file_path:
            validation_file_path = str(
                Path(self.local_storage_cache_path),
                Path(study_id),
                Path(f"{study_id}_validation.tsv"),
            )
        validation_file = Path(validation_file_path).resolve()
        validation_file_path = str(validation_file)

        sub_path = f"/studies/{study_id}/validation-task"

        api_header, error = self.get_api_token()
        headers = {}
        if api_header:
            headers["User-Token"] = api_header
        else:
            return None, error

        api_name = "validation task start"
        try:
            url = f"{self.rest_api_base_url.rstrip('/')}/{sub_path.lstrip('/')}"
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
            for _ in range(retry + 1):
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
            report_url = (
                f"{self.rest_api_base_url.rstrip('/')}/{report_sub_path.lstrip('/')}"
            )
            for _ in range(retry + 1):
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

        validation_file.parent.mkdir(parents=True, exist_ok=True)
        with validation_file.open("w", encoding="utf-8") as f:
            f.write("section\tstatus\tmessage\tdescription\tmetadata_file\n")
            for e in errors:
                f.write(
                    f"{e.section}\t"
                    f"{e.status}\t"
                    f"{e.message}\t"
                    f"{e.description}\t"
                    f"{e.metadata_file}\n"
                )
        return True, status

    def validate_study_v2(
        self,
        study_path: str,
        validation_result_file_path: str,
        pool_period: int = 5,
        retry: int = 20,
        timeout: int = 30,
        validation_api_base_url: Union[None, str] = None,
        rest_api_base_url: Union[None, str] = None,
        api_token: Union[None, str] = None,
    ):
        sub_path = "/study-model/validation"
        auth_sub_path = "/auth/login-with-token"
        provider = MetabolightsStudyProvider(
            db_metadata_collector=None,
            folder_metadata_collector=LocalFolderMetadataCollector(),
        )
        file = Path(study_path)
        basename = file.name
        model: MetabolightsStudyModel = provider.load_study(
            basename,
            study_path=study_path,
            connection=None,
            load_assay_files=True,
            load_sample_file=True,
            load_maf_files=True,
            load_folder_metadata=True,
            calculate_data_folder_size=False,
            calculate_metadata_size=False,
        )
        api_header = api_token
        if not api_token:
            api_header, error = self.get_api_token()
        api_name = "validation v2 get jwt token"
        jwt_token = None
        rest_api_base_url = (
            rest_api_base_url if rest_api_base_url else self.rest_api_base_url
        )

        try:
            url = f"{rest_api_base_url.rstrip('/')}/{auth_sub_path.lstrip('/')}"
            parameters = {}
            response = httpx.post(
                url=url,
                timeout=timeout,
                json={"token": api_header},
                headers={},
                params=parameters,
            )
            success, error = self.check_api_response(api_name, response)
            if not success:
                return None, error
            if "jwt" in response.headers:
                jwt_token = response.headers["jwt"]

            if not jwt_token:
                return (None, "Failure of authentication.")

        except Exception as ex:
            return None, f"Validation task v2 authentication failure: {str(ex)}."

        study_model_str = model.model_dump_json(by_alias=True)
        json_file = io.BytesIO(study_model_str.encode("utf-8"))

        files = {"study_model_json": ("study_model.json", json_file)}

        headers = {"accept": "application/json"}
        headers["Authorization"] = f"Bearer {jwt_token}"
        task_id = None
        api_name = "validation v2 task start"
        validation_api_base_url = (
            validation_api_base_url
            if validation_api_base_url
            else self.validation_api_base_url
        )
        try:
            url = f"{validation_api_base_url.rstrip('/')}/{sub_path.lstrip('/')}"
            parameters = {}
            response = httpx.post(
                url=url,
                timeout=timeout,
                headers=headers,
                files=files,
                params=parameters,
            )
            success, error = self.check_api_response(api_name, response)
            if not success:
                return None, error

            data = json.loads(response.text)
            task_start_response = APIResponse[WorkerTaskStatus].model_validate(
                data, from_attributes=True
            )

            if not task_start_response.content.task_id:
                return (None, f"Failure of {api_name}.")
            task_id = task_start_response.content.task_id
        except Exception as ex:
            return None, f"Validation task v2 start failure: {str(ex)}."

        headers["task_id"] = task_id
        api_name = "validation task v2 status check"
        try:
            task_success = False
            for _ in range(retry + 1):
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
                task_status_response = APIResponse[PolicyResultResponse].model_validate(
                    data, from_attributes=True
                )

                task = task_status_response.content
                status = task.task_status
                if task.task_id and status:
                    if "SUCCESS" in status.upper():
                        task_success = True
                        break
            if not task_success:
                return None, f"Failure of {api_name}."
        except Exception as ex:
            return None, f"{api_name} failure: {str(ex)}."

        result = task_status_response.content.task_result
        with Path(validation_result_file_path).open("w", encoding="utf-8") as f:
            json.dump(result.model_dump(by_alias=True), f, indent=4)

        return True, task_status_response.content.task_id

    def sync_private_ftp_metadata_files(
        self,
        study_id: str,
        pool_period: int = 10,
        retry: int = 10,
        timeout: int = 10,
        user_api_token: Union[None, str] = None,
    ):
        return self.sync_from_private_ftp(
            study_id,
            "metadata",
            pool_period,
            retry,
            timeout,
            user_api_token=user_api_token,
        )

    def sync_private_ftp_data_files(
        self,
        study_id: str,
        pool_period: int = 10,
        retry: int = 1000,
        timeout: int = 10,
        user_api_token: Union[None, str] = None,
    ):
        return self.sync_from_private_ftp(
            study_id, "data", pool_period, retry, timeout, user_api_token=user_api_token
        )

    def sync_from_private_ftp(
        self,
        study_id: str,
        sync_type: Literal["metadata", "data"] = "metadata",
        pool_period: int = 10,
        retry: int = 10,
        timeout: int = 10,
        user_api_token: Union[None, str] = None,
    ):
        sub_path = f"/studies/{study_id}/study-folders/rsync-task"
        if not user_api_token:
            user_api_token, error = self.get_api_token()
        headers = {}
        if user_api_token:
            headers["User-Token"] = user_api_token
        else:
            return None, error
        headers["Dry-Run"] = "false"
        headers["Sync-Type"] = sync_type
        headers["Source-Staging-Area"] = "private-ftp"
        if sync_type == "metadata":
            headers["Target-Staging-Area"] = "rw-study"
        else:
            headers["Target-Staging-Area"] = "readonly-study"

        url = f"{self.rest_api_base_url.rstrip('/')}/{sub_path.lstrip('/')}"
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
            # elif "task" in data and "task_id" in data["task"]:
            #     task_id = data["task"]["task_id"]

            if task_id:
                for _ in range(retry + 1):
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
                return False, "No result"
            else:
                return False, "Response does not have a task id"
        else:
            return (
                (False, response.text)
                if response
                else (False, f"Response code: {str(response.status_code)}")
            )

    def create_submission(
        self,
        user_api_token: Union[None, str] = None,
        timeout: int = 30,
    ) -> Tuple[Union[None, str], Union[None, str]]:
        if not user_api_token:
            user_api_token, error = self.get_api_token()
        headers = {}
        if user_api_token:
            headers["User-Token"] = user_api_token
        else:
            return None, error

        sub_path = "/studies/create"
        url = f"{self.rest_api_base_url.rstrip('/')}/{sub_path.lstrip('/')}"

        try:
            response = httpx.get(url=url, timeout=timeout, headers=headers, params={})
            if response and response.status_code in (200, 201):
                data = json.loads(response.text)
                if "new_study" in data:
                    return data["new_study"], ""

                return None, "Invalid response."
            else:
                return None, response.text if response else "Invalid response."
        except Exception as ex:
            return None, str(ex)

    def create_assay(
        self,
        study_id: str,
        assay_technique: str,
        scan_polarity: str = "",
        column_type: str = "",
        timeout: int = 30,
    ):
        if not study_id or not assay_technique:
            return None, None, "study_id or assay_technique is not defined."

        api_header, error = self.get_api_token()
        headers = {}
        if api_header:
            headers["User-Token"] = api_header
        else:
            return None, None, error

        sub_path = f"/studies/{study_id}/assays"
        url = f"{self.rest_api_base_url.rstrip('/')}/{sub_path.lstrip('/')}"
        body = {"assay": {"type": assay_technique, "columns": []}}
        if scan_polarity:
            body["assay"]["columns"].append(
                {"name": "polarity", "value": scan_polarity.lower()}
            )
        if column_type:
            body["assay"]["columns"].append(
                {"name": "column type", "value": column_type.lower()}
            )
        try:
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
        except Exception as ex:
            return None, None, str(ex)

    def delete_assay(
        self,
        study_id: str,
        assay_filename: str,
        save_audit_copy: bool = True,
        timeout: int = 20,
    ):
        if not study_id or not assay_filename:
            return None, None, "study_id or assay_filename is not defined."

        api_header, error = self.get_api_token()
        headers = {"save_audit_copy": str(save_audit_copy).lower()}
        if api_header:
            headers["User-Token"] = api_header
        else:
            return None, None, error

        sub_path = f"/studies/{study_id}/assays/{assay_filename}"
        url = f"{self.rest_api_base_url.rstrip('/')}/{sub_path.lstrip('/')}"
        try:
            response = httpx.delete(
                url=url,
                timeout=timeout,
                headers=headers,
                params={},
            )
            if response and response.status_code == 404:
                return False, f"{assay_filename} does not exist."
            if response and response.status_code in (200, 201):
                data = json.loads(response.text)
                if "success" in data:
                    return True, None

                return False, "Invalid response."
            else:
                return False, response.text if response else None
        except Exception as ex:
            return False, str(ex)

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
            return LocalDirectory(code=400, message="Invalid study_id")
        if not local_path:
            local_path = self.local_storage_root_path
        local_path = join_path(local_path)
        response = LocalDirectory(root_path=local_path)

        study_id = study_id.upper().strip("/")

        listed_files = []
        requested_files = metadata_files
        if not metadata_files or delete_unlisted_metadata_files:
            result, error = self.list_isa_metadata_files(study_id)
            if result:
                file_names = [x.file for x in result.study]
                descriptors = {x.file: x for x in result.study}
                listed_files = set(file_names)
                if not metadata_files:
                    requested_files = file_names
            else:
                return LocalDirectory(
                    code=404, message="There is no metadata file to download."
                )

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
                    response.actions[key] = "OVERRIDDEN"
                else:
                    local_modified_time = int(os.path.getmtime(file_path))
                    _time = descriptors[filename].created_at
                    try:
                        modified = datetime.datetime.strptime(  # noqa: DTZ007
                            _time, "%Y-%m-%d %H:%M:%S"
                        ).timestamp()
                    except ValueError:
                        modified = 0
                    remote_modified_time = int(modified)
                    if remote_modified_time > local_modified_time:
                        new_requested_files.append(filename)
                        response.actions[key] = "DOWNLOADED"
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
                try:
                    _time = descriptors[filename].created_at
                    try:
                        modified = datetime.datetime.strptime(  # noqa: DTZ007
                            _time, "%Y-%m-%d %H:%M:%S"
                        ).timestamp()
                    except ValueError:
                        modified = 0
                    remote_modified_time = int(modified)
                except Exception:
                    remote_modified_time = None

                success = download_file_from_rest_api(
                    url,
                    new_file_path,
                    timeout=60,
                    headers=headers,
                    parameters=parameters,
                    modification_time=remote_modified_time,
                    is_zip_response=True,
                )
                if not success:
                    response.actions[filename] = "FAILED"
            if delete_unlisted_metadata_files:
                study_path = os.path.join(local_path, study_id)
                if os.path.exists(study_path):
                    for filename in os.listdir(study_path):
                        if filename not in listed_files:
                            file_path = os.path.join(study_path, filename)
                            if is_metadata_file(file_path):
                                response.actions[f"{study_id}/{filename}"] = "DELETED"
                                os.remove(file_path)
            response.success = True
            response.code = 200
            response.message = "Ok"

        except Exception as ex:
            messages.append(
                ErrorMessage(
                    short=f"Download data file {current_file or ''} failure",
                    detail=f"Error message: {str(ex)}",
                )
            )

        return response

    def list_isa_metadata_files(
        self,
        study_id: str,
        user_api_token: Union[str, None] = None,
    ) -> Tuple[Union[StudyResponse, None], Union[None, str]]:
        response, error = self.list_study_directory(
            study_id=study_id, user_api_token=user_api_token
        )
        if response:
            response.study = [
                x for x in response.study if is_metadata_filename_pattern(x.file)
            ]
            return response, None
        else:
            return response, error

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
        url = f"{self.rest_api_base_url.rstrip('/')}/{sub_path.lstrip('/')}"
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
            return None, response.status_code if response else None

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
        self,
        study_id: str,
        subdirectory: Union[str, None] = None,
        timeout=None,
        user_api_token: Union[str, None] = None,
    ) -> Tuple[Union[None, StudyResponse], Union[None, str]]:
        study_id = study_id.upper().strip("/") if study_id else ""
        if not user_api_token:
            user_api_token, error = self.get_api_token()
        headers = {}
        if user_api_token:
            headers["User-Token"] = user_api_token
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
            parameters["directory"] = subdirectory.strip("/")
            paths.append(subdirectory.strip("/"))
        url = f"{self.rest_api_base_url.rstrip('/')}/{sub_path.lstrip('/')}"
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
