from datetime import datetime
from typing import Any, Dict, List, Union

from psycopg2.extras import DictCursor

from metabolights_utils.models.isa.enums import StudyStatus, UserRole, UserStatus
from metabolights_utils.models.isa.study_db_metadata import StudyDBMetadata, Submitter

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


class DbMetadataCollector(object):
    def __init__(self):
        pass

    def get_study_metadata_from_db(self, study_id: str, connection):
        study = self._get_study_from_db(study_id, connection)
        submitters = self._get_study_submitters_from_db(study_id, connection)
        study_db_metadata = self._create_study_db_metadata(study, submitters)
        return study_db_metadata

    def get_all_public_study_ids_from_db(self, connection):
        input = "select acc from studies where status = 3;"
        try:
            cursor = connection.cursor(cursor_factory=DictCursor)
            cursor.execute(input)
            data = cursor.fetchall()
            return data
        except Exception as ex:
            raise ex

    def get_updated_public_study_ids_from_db(
        self,
        connection,
        min_last_update_date: Union[datetime, None] = None,
        max_last_update_date: Union[datetime, None] = None,
    ):
        filter = ["status = 3"]

        if min_last_update_date:
            min_last_update_date_str = min_last_update_date.strftime("%Y-%m-%d")
            filter.append(f"status_date >= '{min_last_update_date_str}'")
        if max_last_update_date:
            max_last_update_date_str = max_last_update_date.strftime("%Y-%m-%d")
            filter.append(f"status_date <= '{max_last_update_date_str}'")
        where_clause = " and ".join(filter)
        input = f"select acc from studies where {where_clause};"
        try:
            cursor = connection.cursor(cursor_factory=DictCursor)
            cursor.execute(input)
            data = cursor.fetchall()
            return data
        except Exception as ex:
            raise ex

    def get_study_ids_from_db(self, connection, sql: str):
        try:
            cursor = connection.cursor(cursor_factory=DictCursor)
            cursor.execute(sql)
            data = cursor.fetchall()
            return data
        except Exception as ex:
            raise ex

    def get_all_study_ids_from_db(self, connection):
        input = "select acc from studies;"
        try:
            cursor = connection.cursor(cursor_factory=DictCursor)
            cursor.execute(input)
            data = cursor.fetchall()
            return data
        except Exception as ex:
            raise ex

    def _get_study_from_db(self, study_id: str, connection):
        input = f"select {', '.join(STUDY_FIELDS)} from studies where acc = %(study_id)s;"
        try:
            cursor = connection.cursor(cursor_factory=DictCursor)
            cursor.execute(input, {"study_id": study_id})
            data = cursor.fetchone()
            return data
        except Exception as ex:
            raise ex

    def _get_study_submitters_from_db(self, study_id: str, connection):
        submitter_fields = [f"u.{field}" for field in SUBMITTER_FIELDS]

        input = f"select {', '.join(submitter_fields)} from studies as s, study_user as su, \
            users as u where su.userid = u.id and su.studyid = s.id and s.acc = %(study_id)s;"
        try:
            cursor = connection.cursor(cursor_factory=DictCursor)
            cursor.execute(input, {"study_id": study_id})
            data = cursor.fetchall()
            if data:
                return [dict(item) for item in data]

            return data
        except Exception as ex:
            raise ex

    def _create_study_db_metadata(self, study, submitters: List[Dict[str, Any]]) -> StudyDBMetadata:
        study_db_metadata: StudyDBMetadata = StudyDBMetadata()
        study_db_metadata.dbId = study["id"] or -1
        study_db_metadata.studyId = study["acc"] or ""
        study_db_metadata.obfuscationCode = study["obfuscationcode"] or ""
        if study_db_metadata.studyId:
            study_no: str = study_db_metadata.studyId.replace("MTBLS", "")
            if study_no.isnumeric():
                study_db_metadata.numericStudyId = int(study_no)
        if study["status"] > -1:
            study_db_metadata.status = StudyStatus.get_from_int(study["status"])

        if study["studytype"] and len(study["studytype"].strip()) > 0:
            study_db_metadata.studyTypes = study["studytype"].strip().split(";")

        if study["override"] and len(study["override"].strip()) > 0:
            override_list = study["override"].strip().split("|")
            overrides = {}
            for item in override_list:
                if item:
                    key_value = item.split(":")
                    if len(key_value) > 1:
                        overrides[key_value[0]] = key_value[1] or ""
            study_db_metadata.overrides = overrides
        study_db_metadata.studySize = int(study["studysize"])
        study_db_metadata.submissionDate = self._get_date_string(study["submissiondate"])
        study_db_metadata.releaseDate = self._get_date_string(study["releasedate"])
        study_db_metadata.updateDate = self._get_date_time_string(study["updatedate"])
        study_db_metadata.statusDate = self._get_date_time_string(study["status_date"])
        study_db_metadata.submitters = self._create_submitters(submitters)
        return study_db_metadata

    def _create_submitters(self, submitters: List[Dict[str, Any]]) -> List[Submitter]:
        if not submitters:
            return []
        submitter_metadata_list = []
        for submitter in submitters:
            submitter_metadata = Submitter()
            submitter_metadata.address = submitter["address"] or ""
            submitter_metadata.affiliation = submitter["affiliation"] or ""
            submitter_metadata.affiliationUrl = submitter["affiliationurl"] or ""
            submitter_metadata.dbId = submitter["id"] or -1
            submitter_metadata.firstName = submitter["firstname"] or ""
            submitter_metadata.lastName = submitter["lastname"] or ""
            submitter_metadata.userName = submitter["username"] or ""
            submitter_metadata.orcid = submitter["orcid"] or ""
            submitter_metadata.joinDate = self._get_date_string(submitter["joindate"])
            submitter_metadata.role = (
                UserRole.get_from_int(submitter["role"])
                if submitter["role"]
                else UserRole.ANONYMOUS
            )
            submitter_metadata.status = (
                UserStatus.get_from_int(submitter["status"])
                if submitter["status"]
                else UserStatus.FROZEN
            )
            submitter_metadata_list.append(submitter_metadata)
        return submitter_metadata_list

    @classmethod
    def _get_date_string(cls, date_value: datetime, pattern: str = "%Y-%m-%d"):
        if not date_value:
            return ""
        return date_value.strftime(pattern)

    @classmethod
    def _get_date_time_string(cls, date_value: datetime):
        if not date_value:
            return ""
        return date_value.isoformat()
