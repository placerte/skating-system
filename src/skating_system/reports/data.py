from __future__ import annotations

from skating_system.reports.models import CompetitionReportData, EventReportData
from skating_system.workbook.models import WorkbookData
from skating_system.workbook.schema import comparison_key


def prepare_report_data(data: WorkbookData) -> EventReportData:
    """Group parsed workbook data while preserving its deterministic order."""

    competitions: list[CompetitionReportData] = []
    for competition in data.competitions:
        key = comparison_key(competition.name)
        judges = tuple(
            judge for judge in data.judges if comparison_key(judge.competition) == key
        )
        entries = tuple(
            entry for entry in data.entries if comparison_key(entry.competition) == key
        )
        competitions.append(
            CompetitionReportData(
                competition=competition,
                judges=judges,
                entries=entries,
                score_sheet=data.score_sheets.get(key),
            )
        )
    return EventReportData(
        metadata=data.metadata,
        competitions=tuple(competitions),
    )
