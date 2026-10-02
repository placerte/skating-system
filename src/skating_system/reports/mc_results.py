from __future__ import annotations

from pathlib import Path

from reportlab.platypus import Flowable

from skating_system.reports.generation import ReportGenerationResult
from skating_system.reports.pdf import (
    PdfMetadata,
    build_pdf,
    heading,
    new_page,
    paragraph,
    report_output_path,
    title,
)
from skating_system.scoring.callback import CallbackResult
from skating_system.services.skating_scorer import SolveResult
from skating_system.services.workbook_compute import (
    ComputedCompetition,
    ComputeResult,
    compute_workbook,
)
from skating_system.workbook.findings import Finding, Severity


def generate_mc_results(
    workbook_path: Path,
    *,
    competition_name: str | None = None,
    output_dir: Path | None = None,
) -> ReportGenerationResult:
    """Generate concise announcement-ready competition results."""

    computed = compute_workbook(workbook_path, competition_name)
    if computed.has_errors:
        return ReportGenerationResult((), computed.findings)
    output_path = report_output_path(
        workbook_path, "mc-results.pdf", output_dir=output_dir
    )
    render_mc_results(computed, output_path)
    findings = (*computed.findings, Finding(Severity.INFO, "MC results generated."))
    return ReportGenerationResult((output_path,), findings)


def render_mc_results(data: ComputeResult, output_path: Path) -> Path:
    """Render one concise announcement page per competition."""

    elements: list[Flowable] = []
    for index, competition in enumerate(data.competitions):
        if index:
            elements.append(new_page())
        elements.extend(_competition_elements(data.event_name, competition))
    return build_pdf(
        output_path,
        elements,
        metadata=PdfMetadata(
            title=f"{data.event_name} - MC Results",
            subject="Announcement-ready competition outcomes",
        ),
    )


def _competition_elements(
    event_name: str,
    computed: ComputedCompetition,
) -> list[Flowable]:
    elements: list[Flowable] = [title(event_name), heading(computed.competition.name)]
    if isinstance(computed.result, SolveResult):
        for placement in computed.result.placements:
            number = computed.entry_numbers[placement.entry_id]
            label = computed.entry_labels[placement.entry_id]
            prefix = f"#{number} — " if number else ""
            elements.append(heading(f"{placement.final_place:g}. {prefix}{label}"))
    elif isinstance(computed.result, CallbackResult):
        elements.append(paragraph("Advancing entries:"))
        advancing = set(computed.result.selection.advancing_entry_ids)
        for tally in computed.result.selection.ordered_tallies:
            if tally.entry_id not in advancing:
                continue
            number = computed.entry_numbers[tally.entry_id]
            label = computed.entry_labels[tally.entry_id]
            prefix = f"#{number} — " if number else ""
            elements.append(heading(f"{prefix}{label}"))
    return elements
