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
    vertical_space,
)
from skating_system.reports.provenance import (
    ReportProvenance,
    collect_report_provenance,
)
from skating_system.scoring.callback import CallbackResult
from skating_system.services.skating_scorer import SolveResult, render_transcript
from skating_system.services.workbook_compute import (
    ComputedCompetition,
    ComputeResult,
    compute_workbook,
)
from skating_system.workbook.findings import Finding, Severity


def generate_management_results(
    workbook_path: Path,
    *,
    competition_name: str | None = None,
    output_dir: Path | None = None,
) -> ReportGenerationResult:
    """Generate a result-reconstruction and provenance audit PDF."""

    computed = compute_workbook(workbook_path, competition_name)
    if computed.has_errors:
        return ReportGenerationResult((), computed.findings)
    provenance = collect_report_provenance(workbook_path)
    output_path = report_output_path(
        workbook_path, "management-results.pdf", output_dir=output_dir
    )
    render_management_results(computed, provenance, output_path)
    findings = (
        *computed.findings,
        Finding(Severity.INFO, "Management results generated."),
    )
    return ReportGenerationResult((output_path,), findings)


def render_management_results(
    data: ComputeResult,
    provenance: ReportProvenance,
    output_path: Path,
) -> Path:
    """Render computed results with identities, derivations, and provenance."""

    elements: list[Flowable] = [
        title(f"{data.event_name} — Management Results"),
        heading("Audit provenance"),
        table(
            ("Field", "Value"),
            (
                ("Validation", "Passed; no blocking errors"),
                ("Generated at (UTC)", provenance.generated_at),
                ("Application version", provenance.application_version),
                ("Commit", provenance.commit),
                ("Workbook", provenance.workbook_filename),
                ("Workbook SHA-256", provenance.workbook_sha256),
            ),
            column_widths=(1.5 * inch, 5.3 * inch),
        ),
    ]
    for competition in data.competitions:
        elements.append(new_page())
        elements.extend(_competition_elements(competition))
    return build_pdf(
        output_path,
        elements,
        metadata=PdfMetadata(
            title=f"{data.event_name} - Management Results",
            subject="Organizer scoring audit and reconstruction record",
        ),
    )


def _competition_elements(computed: ComputedCompetition) -> list[Flowable]:
    elements: list[Flowable] = [
        title(computed.competition.name),
        paragraph(f"Scoring method: {computed.competition.scoring_method.title()}"),
        heading("Judge identity mapping"),
        table(
            ("Public label", "Judge name"),
            (
                (f"Judge {ascii_uppercase[index]}", name)
                for index, name in enumerate(computed.judge_labels.values())
            ),
            column_widths=(1.4 * inch, 5.4 * inch),
        ),
        vertical_space(),
        heading("Raw marks and outcome"),
    ]
    if isinstance(computed.result, SolveResult):
        elements.extend(_skating_elements(computed, computed.result))
    elif isinstance(computed.result, CallbackResult):
        elements.extend(_callback_elements(computed, computed.result))
    return elements


def _skating_elements(
    computed: ComputedCompetition,
    result: SolveResult,
) -> list[Flowable]:
    judge_headers = _judge_headers(len(computed.judge_labels))
    placements = {item.entry_id: item.final_place for item in result.placements}
    elements: list[Flowable] = [
        table(
            ("Number", "Entry", *judge_headers, "Place"),
            (
                (
                    computed.entry_numbers[entry_id],
                    computed.entry_labels[entry_id],
                    *computed.raw_marks_by_entry[entry_id],
                    f"{placements[entry_id]:g}",
                )
                for entry_id in result.derived_table.entry_ids
            ),
        ),
        heading("Derived counts and sums"),
        table(
            ("Entry", "Threshold", "Count", "Sum", "Majority", "Decisive"),
            _derived_rows(computed, result),
        ),
        heading("Rules 5–8 decision transcript"),
    ]
    transcript = render_transcript(result.transcript_root)
    for line in transcript.splitlines():
        if line.strip():
            elements.append(paragraph(line.strip()))
    return elements


def _derived_rows(
    computed: ComputedCompetition,
    result: SolveResult,
) -> list[tuple[object, ...]]:
    rows: list[tuple[object, ...]] = []
    table_data = result.derived_table
    for entry_id in table_data.entry_ids:
        for index, count in enumerate(table_data.counts_by_entry[entry_id]):
            threshold = index + 1
            rows.append(
                (
                    computed.entry_labels[entry_id],
                    threshold,
                    count,
                    table_data.sums_by_entry[entry_id][index],
                    "Yes" if table_data.majorities_by_entry[entry_id][index] else "No",
                    "Yes" if table_data.cutoff_by_entry[entry_id] == threshold else "",
                )
            )
    return rows


def _callback_elements(
    computed: ComputedCompetition,
    result: CallbackResult,
) -> list[Flowable]:
    judge_headers = _judge_headers(len(computed.judge_labels))
    advancing = set(result.selection.advancing_entry_ids)
    policy = result.policy
    return [
        table(
            (
                "Number",
                "Entry",
                *judge_headers,
                "Y",
                "A",
                "N",
                "Total",
                "Outcome",
            ),
            (
                (
                    computed.entry_numbers[tally.entry_id],
                    computed.entry_labels[tally.entry_id],
                    *computed.raw_marks_by_entry[tally.entry_id],
                    tally.yes_count,
                    tally.alternate_count,
                    tally.no_count,
                    f"{tally.total:g}",
                    "Advancing" if tally.entry_id in advancing else "Not advancing",
                )
                for tally in result.selection.ordered_tallies
            ),
        ),
        heading("Callback policy"),
        paragraph(
            "Y=1, A=0.5, N=0; order by total, Yes count, then Alternate "
            f"count; advance count={policy.advance_count}; boundary ties advance; "
            f"Alternate is {'enabled' if policy.alternate_enabled else 'disabled'}."
        ),
    ]


def _judge_headers(judge_count: int) -> tuple[str, ...]:
    return tuple(f"Judge {ascii_uppercase[index]}" for index in range(judge_count))
