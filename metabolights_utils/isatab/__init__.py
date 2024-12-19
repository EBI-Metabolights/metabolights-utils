from functools import lru_cache

from metabolights_utils.isatab import default, reader, writer
from metabolights_utils.isatab.default.factory import (
    DefaultIsaTabReaderFactory,
    DefaultIsaTabWriterFactory,
)
from metabolights_utils.isatab.reader import (
    InvestigationFileReader,
    IsaTableFileReader,
    IsaTabReaderFactory,
)
from metabolights_utils.isatab.writer import (
    InvestigationFileWriter,
    IsaTableFileWriter,
    IsaTabWriterFactory,
)


@lru_cache
def get_reader_factory():
    reader_factory: IsaTabReaderFactory = DefaultIsaTabReaderFactory()
    return reader_factory


@lru_cache
def get_writer_factory():
    writer_factory: IsaTabWriterFactory = DefaultIsaTabWriterFactory()
    return writer_factory


class Reader:
    reader_factory: IsaTabReaderFactory = get_reader_factory()

    @classmethod
    def get_investigation_file_reader(cls) -> InvestigationFileReader:
        return cls.reader_factory.get_investigation_file_reader()

    @classmethod
    def get_assay_file_reader(cls, results_per_page=100) -> IsaTableFileReader:
        return cls.reader_factory.get_assay_file_reader(
            results_per_page=results_per_page
        )

    @classmethod
    def get_sample_file_reader(cls, results_per_page=100) -> IsaTableFileReader:
        return cls.reader_factory.get_assay_file_reader(
            results_per_page=results_per_page
        )

    @classmethod
    def get_assignment_file_reader(cls, results_per_page=100) -> IsaTableFileReader:
        return cls.reader_factory.get_assay_file_reader(
            results_per_page=results_per_page
        )


class Writer:
    writer_factory: IsaTabWriterFactory = get_writer_factory()

    @classmethod
    def get_investigation_file_writer(cls) -> InvestigationFileWriter:
        return cls.writer_factory.get_investigation_file_writer()

    @classmethod
    def get_assay_file_writer(cls) -> IsaTableFileWriter:
        return cls.writer_factory.get_assay_file_writer()

    @classmethod
    def get_sample_file_writer(cls) -> IsaTableFileWriter:
        return cls.writer_factory.get_sample_file_writer()

    @classmethod
    def get_assignment_file_writer(cls) -> IsaTableFileWriter:
        return cls.writer_factory.get_sample_file_writer()


__all__ = [
    "reader",
    "default",
    "writer",
    "Reader",
    "Writer",
    "get_reader_factory",
    "get_writer_factory",
]
