from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest

from skating_system.reports import (
    PdfMetadata,
    build_pdf,
    heading,
    new_page,
    paragraph,
    prepare_report_data,
    report_output_path,
    table,
    title,
)
from skating_system.workbook.reader import read_workbook
from tests.pdf_helpers import inspect_pdf

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_event.xlsx"


def test_generated_pdf_is_readable_and_ordered(tmp_path: Path) -> None:
    output = tmp_path / "reports" / "foundation.pdf"

    build_pdf(
        output,
        [
            title("Retro Boreal 2027"),
            heading("Open Mix & Match"),
            table(
                ("Number", "Entry"),
                (("101", "Alice & Bob"), ("102", "Carol < Dan")),
            ),
            new_page(),
            heading("Solo Jazz Prelims"),
            paragraph("Callback & selection details"),
        ],
        metadata=PdfMetadata(
            title="Foundation Test",
            subject="Shared PDF primitives",
        ),
    )

    inspection = inspect_pdf(output)
    assert output.stat().st_size > 0
    assert inspection.page_count == 2
    assert "Open Mix & Match" in inspection.page_text[0]
    assert inspection.page_text[0].index("101") < inspection.page_text[0].index("102")
    assert "Carol < Dan" in inspection.page_text[0]
    assert "Solo Jazz Prelims" in inspection.page_text[1]
    assert "Page 1" in inspection.page_text[0]
    assert "Page 2" in inspection.page_text[1]
    assert inspection.metadata["/Title"] == "Foundation Test"
    assert inspection.metadata["/Subject"] == "Shared PDF primitives"


def test_identical_input_produces_identical_pdf_bytes(tmp_path: Path) -> None:
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    elements = [title("Stable"), paragraph("Same content")]
    metadata = PdfMetadata(title="Stable Report")

    build_pdf(first, elements, metadata=metadata)
    build_pdf(
        second,
        [title("Stable"), paragraph("Same content")],
        metadata=metadata,
    )

    assert first.read_bytes() == second.read_bytes()


def test_report_data_and_pdf_generation_do_not_modify_workbook(tmp_path: Path) -> None:
    workbook_path = tmp_path / "event.xlsx"
    workbook_path.write_bytes(FIXTURE_PATH.read_bytes())
    before = sha256(workbook_path.read_bytes()).digest()
    read_result = read_workbook(workbook_path, require_score_sheets=False)
    assert read_result.data is not None

    report_data = prepare_report_data(read_result.data)
    output = report_output_path(workbook_path, "summary")
    build_pdf(
        output,
        [
            title(report_data.metadata.event_name),
            *[
                heading(competition.competition.name)
                for competition in report_data.competitions
            ],
        ],
        metadata=PdfMetadata(title="Event Summary"),
    )

    assert [item.competition.name for item in report_data.competitions] == [
        "Open Mix & Match",
        "Solo Jazz Prelims",
    ]
    assert [judge.judge for judge in report_data.competitions[0].judges] == [
        "Jane Smith",
        "Morgan Lee",
        "Sam Roy",
    ]
    assert sha256(workbook_path.read_bytes()).digest() == before
    assert output == tmp_path / "reports" / "summary.pdf"
    assert output.exists()


@pytest.mark.parametrize(
    "filename",
    ["", "../report.pdf", "nested/report.pdf", "nested\\report.pdf"],
)
def test_output_path_rejects_non_filename_values(
    tmp_path: Path,
    filename: str,
) -> None:
    with pytest.raises(ValueError, match="plain filename"):
        report_output_path(tmp_path / "event.xlsx", filename)


def test_pdf_builder_rejects_non_pdf_target(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must end with .pdf"):
        build_pdf(
            tmp_path / "report.txt",
            [paragraph("content")],
            metadata=PdfMetadata(title="Wrong extension"),
        )
