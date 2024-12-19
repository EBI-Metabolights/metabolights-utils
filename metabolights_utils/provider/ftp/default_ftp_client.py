import logging
import os
import re
import shutil
from ftplib import FTP
from typing import List, Set, Union

from metabolights_utils.provider.ftp.model import FtpFolderContent, LocalDirectory
from metabolights_utils.utils.filename_utils import join_path

logger = logging.getLogger(__name__)

code_pattern = re.compile(r"\s*(\d+)\s+(.*)\s*")


class DefaultFtpClient:
    def __init__(
        self,
        local_storage_root_path: str,
        ftp_server_url: str,
        remote_repository_root_directory: str,
        username: Union[str, None] = None,
        password: Union[str, None] = None,
    ) -> None:
        self.ftp_server_url = ftp_server_url
        self.remote_repository_root_directory = (
            remote_repository_root_directory.replace("\\", "").rstrip("/")
        )
        self.local_storage_root_path = local_storage_root_path
        self.username = username if username else ""
        self.password = password if password else ""
        if not os.path.exists(self.local_storage_root_path):
            os.makedirs(self.local_storage_root_path, exist_ok=True)
            logger.info(
                "Local storage root path is created: %s",
                self.local_storage_root_path,
            )
        user = username if username else "anonymous"
        logger.info("Connect to %s  as user %s .", self.ftp_server_url, user)

        self.ftp: Union[None, FTP] = None

    def is_ftp_directory(self, name):
        current = self.ftp.pwd()
        try:
            self.ftp.cwd(name)
            self.ftp.cwd(current)
            return True
        except Exception:
            return False

    def connect(self):
        if not self.ftp:
            self.ftp = FTP(
                self.ftp_server_url,
                timeout=10.0,
                user=self.username,
                passwd=self.password,
            )
        self.ftp.login(user=self.username, passwd=self.password)
        logger.debug("Connected to %s.", self.ftp_server_url)

    def quit(self):
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception as ex:
                logger.exception(
                    "Error while disconnecting FTP server %s: %s.",
                    self.ftp_server_url,
                    str(ex),
                )
            self.ftp = None

    def list_directory(
        self,
        directory: Union[str, None] = None,
        search_pattern: Union[str, None] = None,
    ) -> FtpFolderContent:
        directory = directory.replace("\\", "/").strip("/") if directory else ""
        root_dir = self.remote_repository_root_directory
        remote_directory = f"{root_dir}/{directory}"

        self.connect()

        command = f"LIST {search_pattern}" if search_pattern else "LIST"
        logger.debug("Run command '%s' on %s", command, self.ftp_server_url)
        response: FtpFolderContent = FtpFolderContent(source_directory=remote_directory)
        try:
            self.ftp.cwd(remote_directory)
            return_code = self.ftp.retrlines(command, callback=response.parse_line)
            result = code_pattern.search(return_code)
            if result and result.groups():
                response.code = int(result.groups()[0])
                response.message = result.groups()[1]
            response.success = True
            return response
        except Exception as ex:
            logger.error("FTP directory %s list error: %s", remote_directory, str(ex))
            result = code_pattern.search(str(ex))
            if result and result.groups():
                response.code = int(result.groups()[0])
                response.message = result.groups()[1]
            return response
        finally:
            self.quit()

    def upload_files(
        self,
        remote_directory: Union[str, None] = None,
        file_paths: Union[List[str], None] = None,
    ) -> None:
        remote_directory = remote_directory.strip("/") if remote_directory else ""
        self.connect()

        try:
            self.ftp.cwd(remote_directory)
            for file_path in file_paths:
                filename = os.path.basename(file_path)

                with open(file_path, "rb") as file:
                    self.ftp.storbinary(f"STOR {filename}", file)
            return True, ""
        except Exception as ex:
            message = f"FTP directory {remote_directory} upload error: {str(ex)}"
            logger.error(message)
            return False, message
        finally:
            self.quit()

    def download_file(
        self,
        relative_file_path: str,
        local_path: Union[List[str], None] = None,
        override_local_files: bool = False,
        local_files: Union[LocalDirectory, None] = None,
        skip_files: Union[Set[str], None] = None,
        delete_unlisted_local_files: bool = True,
        keep_local_files: Union[Set[str], None] = None,
    ) -> LocalDirectory:
        local_path = local_path if local_path else self.local_storage_root_path
        local_path = join_path(local_path)
        if local_files is None:
            response = LocalDirectory(root_path=local_path)
        else:
            local_files.root_path = local_path
            response = local_files
        actions = response.actions

        if not relative_file_path or not relative_file_path.strip():
            logger.error("relative_file_path input is not valid.")
            return LocalDirectory(
                root_path=local_path,
                code=451,
                message="root path download does not allowed.",
            )
        if skip_files and relative_file_path in skip_files:
            logger.debug("%s is in skip file list. Skipping...", relative_file_path)
            return response
        remote_root_dir = self.remote_repository_root_directory

        target_path = os.path.join(local_path, relative_file_path)
        parent_path = os.path.dirname(target_path)
        filename = os.path.basename(target_path)

        remote_directory = f"{remote_root_dir}/{relative_file_path}".replace("\\", "/")
        relative_parent_path = os.path.dirname(relative_file_path)

        remote_parent_directory = os.path.dirname(
            os.path.join(remote_root_dir, relative_file_path)
        )
        remote_parent_directory = remote_parent_directory.replace("\\", "/")
        logger.debug("List files within %s on FTP server ", relative_parent_path)
        result = self.list_directory(relative_parent_path, search_pattern=filename)
        is_directory = True
        target_exists = False
        if result.success:
            if (
                result.descriptors
                and len(result.descriptors) == 1
                and result.descriptors[0].base_name == filename
            ):
                is_directory = False
            target_exists = True
        if not target_exists:
            logger.error("%s is not on FTP server.", relative_parent_path)
            return LocalDirectory(
                root_path=local_path, code=result.code, message=result.message
            )
        try:
            if not is_directory:
                self.connect()
                self.ftp.cwd(remote_parent_directory)

                if not os.path.exists(target_path) or override_local_files:
                    if not os.path.exists(parent_path):
                        logger.info("%s folder is created", parent_path)
                        os.makedirs(parent_path, exist_ok=True)
                    with open(target_path, "wb") as local_file:
                        self.ftp.retrbinary("RETR " + filename, local_file.write)
                    actions[relative_file_path] = "DOWNLOADED"
                    logger.debug("%s file is downloaded", relative_file_path)
                else:
                    actions[relative_file_path] = "SKIPPED"
                    logger.debug("%s file exists. Skipping...", relative_file_path)

                response.local_files.append(relative_file_path)
            else:
                if not os.path.exists(target_path):
                    logger.info("%s folder is created", relative_file_path)
                    actions[relative_file_path] = "FOLDER_CREATED"
                    os.makedirs(target_path, exist_ok=True)
                else:
                    actions[relative_file_path] = "FOLDER_SKIPPED"
                    if delete_unlisted_local_files:
                        logger.info("delete_unlisted_local_files is enabled.")
                        local_file_list = os.listdir(target_path)
                        listed_folders = {
                            x.base_name for x in result.descriptors if x.is_directory
                        }
                        listed_files = {
                            x.base_name
                            for x in result.descriptors
                            if not x.is_directory
                        }
                        for item in local_file_list:
                            if item not in listed_folders and item not in listed_files:
                                item_path: str = os.path.join(target_path, item)
                                relative_item_path = (
                                    item_path.replace(f"{local_path}", "")
                                    .strip("/")
                                    .strip("\\")
                                )
                                if keep_local_files and item in keep_local_files:
                                    actions[relative_item_path] = "SKIPPED"
                                    logger.debug(
                                        "%s exists. Skipping", relative_file_path
                                    )
                                    continue
                                try:
                                    if os.path.isdir(item_path):
                                        logger.debug("%s folder is deleted.", item_path)
                                        shutil.rmtree(item_path)
                                        actions[relative_item_path] = "FOLDER_DELETED"
                                    else:
                                        logger.debug("%s file is deleted.", item_path)
                                        os.remove(item_path)
                                        actions[relative_item_path] = "DELETED"
                                except Exception as ex:
                                    logger.error("%s delete error ", item_path, str(ex))

                response.local_folders.append(relative_file_path)
                for collection in (result.folders, result.files):
                    for entry in collection:
                        new_relative_file_path = join_path(
                            relative_file_path, entry
                        ).replace("\\", "/")
                        self.download_file(
                            relative_file_path=new_relative_file_path,
                            local_path=local_path,
                            override_local_files=override_local_files,
                            local_files=response,
                            skip_files=skip_files,
                        )
                        target_path = os.path.join(local_path, relative_file_path)
                        logger.debug(
                            "%s is downloaded on %s", relative_file_path, target_path
                        )
            response.success = True
            response.code = 200
            response.message = "Ok"
        except Exception as ex:
            logger.error(
                "FTP directory %s download error: %s", remote_directory, str(ex)
            )
            response.message = str(ex)
            response.code = 400
        finally:
            self.quit()

        return response
