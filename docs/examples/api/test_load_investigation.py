import logging
import pathlib

from metabolights_utils.isatab import Reader
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    InvestigationFileReaderResult,
)
from metabolights_utils.models.parser.common import ParserReport
from metabolights_utils.models.parser.enums import ParserMessageType

logger = logging.getLogger(__name__)


def test_load_investigation_file():
    file_path = pathlib.Path("tests/test-data/MTBLS1/i_Investigation.txt")
    reader: InvestigationFileReader = Reader.get_investigation_file_reader()
    result: InvestigationFileReaderResult = reader.read(file_buffer_or_path=file_path)
    report: ParserReport = result.parser_report
    for message in report.messages:
        if message.type in (ParserMessageType.ERROR, ParserMessageType.CRITICAL):
            logger.error("%s %s %s", message.section, message.short, message.detail)
        else:
            logger.debug("%s %s %s", message.section, message.short, message.detail)
    investigation = result.investigation
    assert investigation.studies
    if investigation.studies:
        logger.info("Study title: %", investigation.studies[0].title)
