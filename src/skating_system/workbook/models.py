from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EventMetadata:
    """Workbook-level event metadata."""

    schema_version: str
    event_name: str


@dataclass(frozen=True)
class Competition:
    """A competition declared in the workbook."""

    name: str
    scoring_method: str
    alternate_enabled: bool = False
    status: str = ""
    notes: str = ""
    source_row: int = 0


@dataclass(frozen=True)
class JudgeAssignment:
    """A human-readable judge assigned to a competition."""

    competition: str
    judge: str
    order: int | None = None
    source_row: int = 0


@dataclass(frozen=True)
class EntryAssignment:
    """A human-readable entry assigned to a competition."""

    competition: str
    entry: str
    number: str = ""
    order: int | None = None
    source_row: int = 0


@dataclass(frozen=True)
class MarkValue:
    """One raw judge mark and its workbook location."""

    value: object
    cell: str


@dataclass(frozen=True)
class ScoreRow:
    """One entry row from a generated score sheet."""

    entry: str
    number: str
    marks: dict[str, MarkValue]
    source_row: int


@dataclass(frozen=True)
class ScoreSheet:
    """Raw method-specific marks for one competition."""

    competition: str
    sheet_name: str
    judges: tuple[str, ...]
    rows: tuple[ScoreRow, ...]


@dataclass(frozen=True)
class WorkbookData:
    """Parsed workbook data before method-specific scoring conversion."""

    path: Path
    metadata: EventMetadata
    competitions: tuple[Competition, ...]
    judges: tuple[JudgeAssignment, ...]
    entries: tuple[EntryAssignment, ...]
    score_sheets: dict[str, ScoreSheet]
