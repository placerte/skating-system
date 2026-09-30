from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from openpyxl import load_workbook

from skating_system.cli import main
from skating_system.reports import generate_judge_cards
from tests.pdf_helpers import inspect_pdf

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_event.xlsx"


def test_judge_cards_include_every_assignment_and_ordered_entries(
    tmp_path: Path,
) -> None:
    workbook_path = tmp_path / "event.xlsx"
    workbook_path.write_bytes(FIXTURE_PATH.read_bytes())
    before = sha256(workbook_path.read_bytes()).digest()

    result = generate_judge_cards(workbook_path)

    assert not result.has_errors
    inspection = inspect_pdf(result.output_paths[0])
    assert inspection.page_count == 6
    for page, judge in zip(
        inspection.page_text[:3],
        ("Jane Smith", "Morgan Lee", "Sam Roy"),
        strict=True,
    ):
        assert "Open Mix & Match" in page
        assert f"Judge: {judge}" in page
        assert "Rank 1 is best" in page
        assert "do not duplicate ranks" in page
        assert page.count("Alice Tremblay & Bob Smith") == 1
        assert page.count("Carol Nguyen & Dan Roy") == 1
        assert page.index("101") < page.index("102")
    for page, judge in zip(
        inspection.page_text[3:],
        ("Jane Smith", "Morgan Lee", "Sam Roy"),
        strict=True,
    ):
        assert "Solo Jazz Prelims" in page
        assert f"Judge: {judge}" in page
        assert "Yes" in page
        assert "No" in page
        assert "Alternate" in page
        assert "Mark Yes or No for every entry." in page
        assert "Use Alternate only when needed." in page
        assert page.count("Evelyn Chen") == 1
        assert page.count("Frank Martin") == 1
        assert page.index("\n201\n") < page.index("\n202\n")
    assert sha256(workbook_path.read_bytes()).digest() == before


def test_callback_card_omits_alternate_when_disabled(tmp_path: Path) -> None:
    workbook_path = tmp_path / "event.xlsx"
    workbook_path.write_bytes(FIXTURE_PATH.read_bytes())
    workbook = load_workbook(workbook_path)
    competitions = workbook["Competitions"]
    competitions["C3"] = False
    workbook.save(workbook_path)
    workbook.close()

    result = generate_judge_cards(workbook_path)

    assert not result.has_errors
    inspection = inspect_pdf(result.output_paths[0])
    for page in inspection.page_text[3:]:
        assert "Yes" in page
        assert "No" in page
        assert "Alternate" not in page
        assert "Mark Yes or No for every entry." in page


def test_pre_event_cli_generates_both_documents(
    tmp_path: Path,
    capsys,
) -> None:
    workbook_path = tmp_path / "event.xlsx"
    workbook_path.write_bytes(FIXTURE_PATH.read_bytes())

    assert main(["generate", "pre-event", str(workbook_path)]) == 0

    output = capsys.readouterr().out
    call_sheets = tmp_path / "reports" / "call-sheets.pdf"
    judge_cards = tmp_path / "reports" / "judge-cards.pdf"
    assert f"OUTPUT: {call_sheets}" in output
    assert f"OUTPUT: {judge_cards}" in output
    assert call_sheets.exists()
    assert judge_cards.exists()
