from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


@dataclass(frozen=True)
class ReportProvenance:
    generated_at: str
    application_version: str
    commit: str
    workbook_filename: str
    workbook_sha256: str


def collect_report_provenance(workbook_path: Path) -> ReportProvenance:
    """Collect audit metadata without changing the workbook."""

    return ReportProvenance(
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        application_version=_application_version(),
        commit=_commit_identifier(),
        workbook_filename=workbook_path.name,
        workbook_sha256=sha256(workbook_path.read_bytes()).hexdigest(),
    )


def _application_version() -> str:
    try:
        return version("skating-system")
    except PackageNotFoundError:
        return "unknown"


def _commit_identifier() -> str:
    repository = Path(__file__).resolve().parents[3]
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"
