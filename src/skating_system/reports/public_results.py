from __future__ import annotations

from pathlib import Path
from string import ascii_uppercase

from reportlab.lib.units import inch
from reportlab.platypus import Flowable

from skating_system.reports.generation import ReportGenerationResult
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
from skating_system.scoring.callback import CallbackResult
from skating_system.services.skating_scorer import SolveResult
from skating_system.services.workbook_compute import (
    ComputedCompetition,
    ComputeResult,
    compute_workbook,
)
from skating_system.workbook.findings import Finding, Severity


def generate_public_results(
    workbook_path: Path,
    *,
    competition_name: str | None = None,
    output_dir: Path | None = None,
) -> ReportGenerationResult:
    """Validate, compute, and generate an anonymous public results PDF."""

    computed = compute_workbook(workbook_path, competition_name)
    if computed.has_errors:
        return ReportGenerationResult((), computed.findings)
    output_path = report_output_path(
        workbook_path,
        "public-results.pdf",
        output_dir=output_dir,
    )
    render_public_results(computed, output_path)
    findings = (*computed.findings, Finding(Severity.INFO, "Public results generated."))
    return ReportGenerationResult((output_path,), findings)


def render_public_results(data: ComputeResult, output_path: Path) -> Path:
    """Render computed results without including judge identities."""

    elements: list[Flowable] = []
    for index, competition in enumerate(data.competitions):
        if index:
            elements.append(new_page())
        elements.extend(_competition_elements(data.event_name, competition))
    return build_pdf(
        output_path,
        elements,
        metadata=PdfMetadata(
            title=f"{data.event_name} - Public Results",
            subject="Anonymous competition marks and final outcomes",
        ),
    )


def _competition_elements(
    event_name: str,
    computed: ComputedCompetition,
) -> list[Flowable]:
    competition = computed.competition
    judge_headers = [
        f"Judge {ascii_uppercase[index]}" for index in range(len(computed.judge_labels))
    ]
    elements: list[Flowable] = [
        title(event_name),
        heading(competition.name),
        paragraph(f"Scoring method: {competition.scoring_method.title()}"),
    ]
    if isinstance(computed.result, SolveResult):
        placements = {
            item.entry_id: f"Place {item.final_place:g}"
            for item in computed.result.placements
        }
        entry_order = [item.entry_id for item in computed.result.placements]
        elements.append(
            table(
                ("Number", "Entry", *judge_headers, "Final result"),
                (
                    (
                        computed.entry_numbers[entry_id],
                        computed.entry_labels[entry_id],
                        *computed.raw_marks_by_entry[entry_id],
                        placements[entry_id],
                    )
                    for entry_id in entry_order
                ),
                column_widths=_column_widths(len(judge_headers)),
            )
        )
        elements.append(
            paragraph(
                "Ranks are resolved using the audited Skating System Rules 5–8. "
                "Detailed resolution transcripts are retained in management reports."
            )
        )
    elif isinstance(computed.result, CallbackResult):
        advancing = set(computed.result.selection.advancing_entry_ids)
        elements.append(
            table(
                ("Number", "Entry", *judge_headers, "Total", "Outcome"),
                (
                    (
                        computed.entry_numbers[tally.entry_id],
                        computed.entry_labels[tally.entry_id],
                        *computed.raw_marks_by_entry[tally.entry_id],
                        f"{tally.total:g}",
                        "Advancing" if tally.entry_id in advancing else "Not advancing",
                    )
                    for tally in computed.result.selection.ordered_tallies
                ),
                column_widths=_column_widths(len(judge_headers), callback=True),
            )
        )
        policy = computed.result.policy
        alternate = "enabled" if policy.alternate_enabled else "disabled"
        elements.append(
            paragraph(
                "Callback policy: Y=1, A=0.5, N=0; order by total, Yes count, "
                f"then Alternate count; advance count={policy.advance_count}; "
                f"boundary ties advance; Alternate is {alternate}."
            )
        )
    return elements


def _column_widths(judge_count: int, *, callback: bool = False) -> tuple[float, ...]:
    fixed_width = 0.6 * inch + 2.0 * inch
    outcome_width = 1.0 * inch
    if callback:
        outcome_width = 1.7 * inch
    judge_width = max(
        0.45 * inch, (7.0 * inch - fixed_width - outcome_width) / judge_count
    )
    widths = [0.6 * inch, 2.0 * inch]
    widths.extend([judge_width] * judge_count)
    if callback:
        widths.extend([0.6 * inch, 1.1 * inch])
    else:
        widths.append(outcome_width)
    return tuple(widths)
