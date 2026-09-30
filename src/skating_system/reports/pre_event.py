from __future__ import annotations

from pathlib import Path

from skating_system.reports.call_sheets import render_call_sheets
from skating_system.reports.generation import (
    ReportGenerationResult,
    load_report_source,
)
from skating_system.reports.judge_cards import render_judge_cards
from skating_system.reports.pdf import report_output_path
from skating_system.workbook.findings import Finding, Severity


def generate_pre_event_documents(
    workbook_path: Path,
    *,
    output_dir: Path | None = None,
) -> ReportGenerationResult:
    """Generate all documents needed before competition marks exist."""

    source = load_report_source(workbook_path)
    if source.data is None:
        return ReportGenerationResult((), source.findings)

    call_sheets_path = report_output_path(
        workbook_path,
        "call-sheets.pdf",
        output_dir=output_dir,
    )
    judge_cards_path = report_output_path(
        workbook_path,
        "judge-cards.pdf",
        output_dir=output_dir,
    )
    render_call_sheets(source.data, call_sheets_path)
    render_judge_cards(source.data, judge_cards_path)
    findings = (
        *source.findings,
        Finding(Severity.INFO, "Pre-event documents generated."),
    )
    return ReportGenerationResult(
        (call_sheets_path, judge_cards_path),
        findings,
    )
