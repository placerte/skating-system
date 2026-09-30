from __future__ import annotations

from dataclasses import dataclass

from skating_system.workbook.models import (
    Competition,
    EntryAssignment,
    EventMetadata,
    JudgeAssignment,
    ScoreSheet,
)


@dataclass(frozen=True)
class CompetitionReportData:
    """Ordered parsed data available to one competition report section."""

    competition: Competition
    judges: tuple[JudgeAssignment, ...]
    entries: tuple[EntryAssignment, ...]
    score_sheet: ScoreSheet | None


@dataclass(frozen=True)
class EventReportData:
    """Parsed event data prepared for deterministic report rendering."""

    metadata: EventMetadata
    competitions: tuple[CompetitionReportData, ...]
