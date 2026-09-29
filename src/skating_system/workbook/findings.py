from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    """Severity of one workbook validation finding."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass(frozen=True)
class Finding:
    """An actionable workbook parsing or validation result."""

    severity: Severity
    message: str
    sheet: str | None = None
    cell: str | None = None
    competition: str | None = None
    judge: str | None = None
    entry: str | None = None

    def format(self) -> str:
        """Format the finding for terminal output."""

        location = ""
        if self.sheet and self.cell:
            location = f" ({self.sheet}!{self.cell})"
        elif self.sheet:
            location = f" ({self.sheet})"
        return f"{self.severity}: {self.message}{location}"


@dataclass(frozen=True)
class ValidationReport:
    """All findings from a workbook validation run."""

    findings: tuple[Finding, ...]

    @property
    def has_errors(self) -> bool:
        return any(finding.severity is Severity.ERROR for finding in self.findings)
