from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from skating_system.cli import main
from skating_system.reports import generate_call_sheets
from tests.pdf_helpers import inspect_pdf

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_event.xlsx"


def test_call_sheets_include_each_competition_and_entry_in_order(
    tmp_path: Path,
) -> None:
    workbook_path = tmp_path / "event.xlsx"
    workbook_path.write_bytes(FIXTURE_PATH.read_bytes())
    before = sha256(workbook_path.read_bytes()).digest()

    result = generate_call_sheets(workbook_path)

    assert not result.has_errors
    assert result.output_paths == (tmp_path / "reports" / "call-sheets.pdf",)
    inspection = inspect_pdf(result.output_paths[0])
    assert inspection.page_count == 2
    first, second = inspection.page_text
    assert "Retro Boreal 2027" in first
    assert "Open Mix & Match" in first
    assert "Scoring method: Skating" in first
    assert first.count("Alice Tremblay & Bob Smith") == 1
    assert first.count("Carol Nguyen & Dan Roy") == 1
    assert first.index("101") < first.index("102")
    assert "Manual notes:" in first
    assert "Solo Jazz Prelims" in second
    assert "Scoring method: Callback" in second
    assert second.count("Evelyn Chen") == 1
    assert second.count("Frank Martin") == 1
    assert second.index("\n201\n") < second.index("\n202\n")
    assert sha256(workbook_path.read_bytes()).digest() == before


def test_call_sheets_cli_reports_output(tmp_path: Path, capsys) -> None:
    workbook_path = tmp_path / "event.xlsx"
    workbook_path.write_bytes(FIXTURE_PATH.read_bytes())

    assert main(["generate", "call-sheets", str(workbook_path)]) == 0

    output = capsys.readouterr().out
    assert f"OUTPUT: {tmp_path / 'reports' / 'call-sheets.pdf'}" in output
    assert "INFO: Call sheets generated." in output
