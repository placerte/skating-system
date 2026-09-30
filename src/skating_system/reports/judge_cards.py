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
)
from skating_system.workbook.findings import Finding, Severity
from skating_system.workbook.schema import SCORING_METHOD_SKATING


# GitHub issue #7: printable scorecards for each judge assignment.
def generate_judge_cards(
    workbook_path: Path,
    *,
    output_dir: Path | None = None,
) -> ReportGenerationResult:
    """Generate one ordered scorecard for every assigned judge."""

    source = load_report_source(workbook_path)
    if source.data is None:
        return ReportGenerationResult((), source.findings)

    output_path = report_output_path(
        workbook_path,
        "judge-cards.pdf",
        output_dir=output_dir,
    )
    render_judge_cards(source.data, output_path)
    findings = (*source.findings, Finding(Severity.INFO, "Judge cards generated."))
    return ReportGenerationResult((output_path,), findings)


def render_judge_cards(data: EventReportData, output_path: Path) -> Path:
    """Render validated event data to a judge-cards PDF."""

    elements: list[Flowable] = []
    card_index = 0
    for competition_data in data.competitions:
        competition = competition_data.competition
        for judge in competition_data.judges:
            if card_index:
                elements.append(new_page())
            card_index += 1
            elements.extend(
                [
                    title(data.metadata.event_name),
                    heading(competition.name),
                    paragraph(f"Judge: {judge.judge}"),
                    paragraph(f"Scoring method: {competition.scoring_method.title()}"),
                ]
            )
            if competition.scoring_method == SCORING_METHOD_SKATING:
                elements.extend(
                    [
                        paragraph(
                            "Rank every entry exactly once. Rank 1 is best; "
                            "do not duplicate ranks."
                        ),
                        table(
                            ("Number", "Entry", "Rank"),
                            (
                                (entry.number, entry.entry, "")
                                for entry in competition_data.entries
                            ),
                            column_widths=(0.9 * inch, 4.9 * inch, 1.1 * inch),
                        ),
                    ]
                )
            else:
                headers = ["Number", "Entry", "Yes", "No"]
                if competition.alternate_enabled:
                    headers.append("Alternate")
                instruction = "Mark Yes or No for every entry."
                if competition.alternate_enabled:
                    instruction += " Use Alternate only when needed."
                elements.extend(
                    [
                        paragraph(instruction),
                        table(
                            headers,
                            (
                                (
                                    entry.number,
                                    entry.entry,
                                    *([""] * (len(headers) - 2)),
                                )
                                for entry in competition_data.entries
                            ),
                            column_widths=_callback_widths(
                                competition.alternate_enabled
                            ),
                        ),
                    ]
                )

    return build_pdf(
        output_path,
        elements,
        metadata=PdfMetadata(
            title=f"{data.metadata.event_name} - Judge Scorecards",
            subject="Judge scorecards",
        ),
    )


def _callback_widths(alternate_enabled: bool) -> tuple[float, ...]:
    if alternate_enabled:
        return (0.8 * inch, 3.4 * inch, 0.7 * inch, 0.7 * inch, 1.3 * inch)
    return (0.9 * inch, 4.4 * inch, 0.8 * inch, 0.8 * inch)
