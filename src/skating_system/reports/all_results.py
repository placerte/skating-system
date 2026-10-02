from __future__ import annotations

from pathlib import Path

from skating_system.reports.generation import ReportGenerationResult
from skating_system.reports.management_results import generate_management_results
from skating_system.reports.mc_results import generate_mc_results
from skating_system.reports.public_results import generate_public_results


def generate_all_results(
    workbook_path: Path,
    *,
    competition_name: str | None = None,
    output_dir: Path | None = None,
) -> ReportGenerationResult:
    """Generate public, management, and MC result PDFs."""

    generators = (
        generate_public_results,
        generate_management_results,
        generate_mc_results,
    )
    output_paths: list[Path] = []
    findings = []
    for generator in generators:
        result = generator(
            workbook_path,
            competition_name=competition_name,
            output_dir=output_dir,
        )
        output_paths.extend(result.output_paths)
        findings.extend(result.findings)
        if result.has_errors:
            break
    return ReportGenerationResult(tuple(output_paths), tuple(findings))
