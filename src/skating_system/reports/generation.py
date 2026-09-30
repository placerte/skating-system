from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skating_system.reports.data import prepare_report_data
from skating_system.reports.models import EventReportData
from skating_system.workbook.findings import Finding, Severity
from skating_system.workbook.reader import read_workbook
from skating_system.workbook.validation import validate_setup_data


@dataclass(frozen=True)
class ReportGenerationResult:
    """Outputs and workbook findings from a report generation command."""

    output_paths: tuple[Path, ...]
    findings: tuple[Finding, ...]

    @property
    def has_errors(self) -> bool:
        return any(finding.severity is Severity.ERROR for finding in self.findings)


@dataclass(frozen=True)
class ReportSource:
    """Validated, ordered workbook data ready for report rendering."""

    data: EventReportData | None
    findings: tuple[Finding, ...]

    @property
    def has_errors(self) -> bool:
        return any(finding.severity is Severity.ERROR for finding in self.findings)


def load_report_source(workbook_path: Path) -> ReportSource:
    """Read and validate setup data without requiring score-entry sheets."""

    read_result = read_workbook(
        workbook_path,
        require_score_sheets=False,
        read_score_sheets=False,
    )
    findings = list(read_result.findings)
    if read_result.data is None:
        return ReportSource(data=None, findings=tuple(findings))

    setup_findings, _ = validate_setup_data(read_result.data)
    findings.extend(setup_findings)
    if not read_result.data.competitions:
        findings.append(
            Finding(Severity.ERROR, "No competitions are available for reporting.")
        )
    if any(finding.severity is Severity.ERROR for finding in findings):
        return ReportSource(data=None, findings=tuple(findings))

    return ReportSource(
        data=prepare_report_data(read_result.data),
        findings=tuple(findings),
    )
