import os
import pathlib
import shutil

from metabolights_utils.isatab import Reader, Writer
from metabolights_utils.isatab.reader import (
    IsaTableFileReader,
    IsaTableFileReaderResult,
)
from metabolights_utils.isatab.writer import IsaTableFileWriter


def test_assay_metadata_file_read_write():
    path_original = pathlib.Path(
        "tests/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    file_path = (
        ".test-temp/test-data/MTBLS1/a_MTBLS1_metabolite_profiling_NMR_spectroscopy.txt"
    )
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    shutil.copy(path_original, file_path)
    helper: IsaTableFileReader = Reader.get_assay_file_reader()
    # with default results_per_page value - 100

    with open(file_path, "r") as file_buffer:
        result: IsaTableFileReaderResult = helper.get_page(
            file_buffer=file_buffer,
            page=2,
            results_per_page=50,
            file_path=str(file_path),
            selected_columns=[
                "Sample Name",
                "Derived Spectral Data File",
                "Metabolite Assignment File",
            ],
        )
        assert len(result.parser_report.messages) == 0
        assert result.isa_table_file.table.row_count == 50
        assert len(result.isa_table_file.table.columns) == 3
    writer: IsaTableFileWriter = Writer.get_assay_file_writer()
    sha256 = "6ea4c731ce35165f83a5d30438cd8753a6afa5fa9a1109893ffc1c213b1da869"
    isa_table = result.isa_table_file.table
    report = writer.save_isa_table(
        file_path=str(file_path), file_sha256_hash=sha256, isa_table=isa_table
    )
    assert report.success

    first_column = result.isa_table_file.table.columns[0]
    result.isa_table_file.table.data[first_column][0] = "Updated Sample Name"
    report = writer.save_isa_table(
        file_path=str(file_path), file_sha256_hash=sha256, isa_table=isa_table
    )
    assert report.success
    assert report.updated_file_sha256_hash != sha256
    assert not report.message
