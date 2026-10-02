from __future__ import annotations

from pathlib import Path

from skating_system.cli import main
from skating_system.reports.public_results import generate_public_results
from tests.pdf_helpers import inspect_pdf
from tests.test_workbook_compute import _completed_workbook


JUDGE_NAMES = ("Jane Smith", "Morgan Lee", "Sam Roy")


def test_public_results_are_anonymous_and_match_computed_outcomes(
    tmp_path: Path,
) -> None:
    workbook_path = _completed_workbook(tmp_path)

    result = generate_public_results(workbook_path)

    assert not result.has_errors
    assert len(result.output_paths) == 1
    output_path = result.output_paths[0]
    inspection = inspect_pdf(output_path)
    assert output_path.name == "public-results.pdf"
    assert inspection.page_count == 2
    assert "Judge A" in inspection.text
    assert "Judge B" in inspection.text
    assert "Judge C" in inspection.text
    assert "Place 1" in inspection.text
    assert "1\n1\n1" in inspection.text
    assert "Advancing" in inspection.text
    assert "Y\nY\nA" in inspection.text
    assert "Y=1, A=0.5, N=0" in inspection.text
    assert "Detailed resolution transcripts" in inspection.text
    all_public_data = (
        inspection.text
        + "\n"
        + "\n".join(inspection.metadata.values())
        + "\n"
        + output_path.name
    )
    for judge_name in JUDGE_NAMES:
        assert judge_name not in all_public_data
        assert judge_name.encode() not in output_path.read_bytes()


def test_public_results_can_filter_one_competition(tmp_path: Path) -> None:
    workbook_path = _completed_workbook(tmp_path)

    result = generate_public_results(
        workbook_path,
        competition_name="Solo Jazz Prelims",
        output_dir=tmp_path / "published",
    )

    assert not result.has_errors
    inspection = inspect_pdf(result.output_paths[0])
    assert inspection.page_count == 1
    assert "Solo Jazz Prelims" in inspection.text
    assert "Open Mix & Match" not in inspection.text


def test_public_report_cli_generates_pdf(tmp_path: Path, capsys) -> None:
    workbook_path = _completed_workbook(tmp_path)

    exit_code = main(
        [
            "report",
            "public",
            str(workbook_path),
            "--competition",
            "Open Mix & Match",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "OUTPUT:" in output
    assert "public-results.pdf" in output
