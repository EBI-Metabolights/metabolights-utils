import os
import pathlib
import uuid

from metabolights_utils.isatab.helper.investigation_file_helper import InvestigationFileHelper
from metabolights_utils.isatab.investigation_file_reader import InvestigationFileReaderResult
from metabolights_utils.isatab.isatab_file_helper import IsaTabFileHelper


def test_investigation_file_success_01():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    helper: InvestigationFileHelper = IsaTabFileHelper.get_investigation_file_reader()
    result: InvestigationFileReaderResult = helper.read(file_path=file_path)
    assert len(result.investigation.studies) == 1

    tmp_file_name = uuid.uuid4().hex
    tmp_path = pathlib.Path(f"/tmp/test_{tmp_file_name}.txt")
    helper.write(result.investigation, file_path=tmp_path)

    with open(tmp_path, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
    os.remove(tmp_path)
