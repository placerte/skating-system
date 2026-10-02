from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from skating_system.cli import main
from skating_system.reports.all_results import generate_all_results
from skating_system.reports.management_results import generate_management_results
from skating_system.reports.mc_results import generate_mc_results
from skating_system.reports.public_results import generate_public_results
from tests.pdf_helpers import inspect_pdf
from tests.test_workbook_compute import _completed_workbook


def test_management_report_contains_reconstruction_and_provenance(
    tmp_path: Path,
) -> None:
    workbook_path = _completed_workbook(tmp_path)
    expected_hash = sha256(workbook_path.read_bytes()).hexdigest()

    result = generate_management_results(workbook_path)

    assert not result.has_errors
    inspection = inspect_pdf(result.output_paths[0])
    assert inspection.page_count >= 3
    assert "Passed; no blocking errors" in inspection.text
    assert workbook_path.name in inspection.text
    assert expected_hash in inspection.text.replace("\n", "")
    assert "Application version" in inspection.text
    assert "Commit" in inspection.text
    assert "Jane Smith" in inspection.text
    assert "Judge A" in inspection.text
    assert "Derived counts and sums" in inspection.text
    assert "Rules 5–8 decision transcript" in inspection.text
    assert "Callback policy" in inspection.text
    assert "Y=1, A=0.5, N=0" in inspection.text


def test_mc_report_is_concise_and_one_page_per_competition(tmp_path: Path) -> None:
    workbook_path = _completed_workbook(tmp_path)

    result = generate_mc_results(workbook_path)

    assert not result.has_errors
    inspection = inspect_pdf(result.output_paths[0])
    assert inspection.page_count == 2
    assert "Open Mix & Match" in inspection.page_text[0]
    assert "Solo Jazz Prelims" in inspection.page_text[1]
    assert "1. #101 — Alice Tremblay & Bob Smith" in inspection.page_text[0]
    assert "#201 — Evelyn Chen" in inspection.page_text[1]
    for unnecessary_detail in (
        "Judge A",
        "Jane Smith",
        "Callback policy",
        "decision transcript",
        "SHA-256",
    ):
        assert unnecessary_detail not in inspection.text


def test_management_and_public_reports_agree_and_do_not_modify_workbook(
    tmp_path: Path,
) -> None:
    workbook_path = _completed_workbook(tmp_path)
    before = sha256(workbook_path.read_bytes()).digest()

    management = generate_management_results(workbook_path)
    public = generate_public_results(workbook_path)

    management_text = inspect_pdf(management.output_paths[0]).text
    public_text = inspect_pdf(public.output_paths[0]).text
    normalized_management = " ".join(management_text.split())
    normalized_public = " ".join(public_text.split())
    for expected in (
        "Alice Tremblay & Bob Smith",
        "Evelyn Chen",
        "1 1 1",
        "Y Y A",
        "Advancing",
    ):
        assert expected in normalized_management
        assert expected in normalized_public
    assert sha256(workbook_path.read_bytes()).digest() == before


def test_report_all_and_cli_generate_three_artifacts(
    tmp_path: Path,
    capsys,
) -> None:
    workbook_path = _completed_workbook(tmp_path)
    output_dir = tmp_path / "direct"

    direct = generate_all_results(workbook_path, output_dir=output_dir)

    assert not direct.has_errors
    assert {path.name for path in direct.output_paths} == {
        "public-results.pdf",
        "management-results.pdf",
        "mc-results.pdf",
    }
    assert main(["report", "all", str(workbook_path)]) == 0
    output = capsys.readouterr().out
    assert output.count("OUTPUT:") == 3
