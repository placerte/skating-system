from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch
from reportlab.platypus import Flowable

from skating_system.reports.generation import (
    ReportGenerationResult,
    load_report_source,
)
from skating_system.reports.models import EventReportData
from skating_system.reports.pdf import (
    PdfMetadata,
    build_pdf,
    heading,
    new_page,
    paragraph,
    report_output_path,
    table,
    title,
    vertical_space,
)
from skating_system.workbook.findings import Finding, Severity


# GitHub issue #6: printable competition call sheets.
def generate_call_sheets(
    workbook_path: Path,
    *,
    output_dir: Path | None = None,
) -> ReportGenerationResult:
    """Generate one ordered competitor call sheet per competition."""

    source = load_report_source(workbook_path)
    if source.data is None:
        return ReportGenerationResult((), source.findings)

    output_path = report_output_path(
        workbook_path,
        "call-sheets.pdf",
        output_dir=output_dir,
    )
    render_call_sheets(source.data, output_path)
    findings = (*source.findings, Finding(Severity.INFO, "Call sheets generated."))
    return ReportGenerationResult((output_path,), findings)


def render_call_sheets(data: EventReportData, output_path: Path) -> Path:
    """Render validated event data to a call-sheets PDF."""

    elements: list[Flowable] = []
    for index, competition_data in enumerate(data.competitions):
        competition = competition_data.competition
        if index:
            elements.append(new_page())
        elements.extend(
            [
                title(data.metadata.event_name),
                heading(competition.name),
                paragraph(f"Scoring method: {competition.scoring_method.title()}"),
                table(
                    ("Called", "Number", "Entry", "Notes"),
                    (
                        ("[ ]", entry.number, entry.entry, "")
                        for entry in competition_data.entries
                    ),
                    column_widths=(0.55 * inch, 0.75 * inch, 3.35 * inch, 2.25 * inch),
                ),
                vertical_space(12),
                paragraph("Manual notes:"),
                paragraph("________________________________________________________"),
                paragraph("________________________________________________________"),
            ]
        )

    return build_pdf(
        output_path,
        elements,
        metadata=PdfMetadata(
            title=f"{data.metadata.event_name} - Competitor Call Sheets",
            subject="Ordered competitor call sheets",
        ),
    )
