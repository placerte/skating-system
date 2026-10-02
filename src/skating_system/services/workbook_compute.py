from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid5

from skating_system.domain.models import Competition as SkatingCompetition
from skating_system.domain.models import RankMark
from skating_system.scoring.callback import (
    CallbackMark,
    CallbackPolicy,
    CallbackResult,
    compute_callback_result,
)
from skating_system.services.skating_scorer import SolveResult, compute_solve_result
from skating_system.workbook.findings import Finding, Severity
from skating_system.workbook.models import Competition, MarkValue, WorkbookData
from skating_system.workbook.reader import read_workbook
from skating_system.workbook.schema import (
    SCORING_METHOD_CALLBACK,
    SCORING_METHOD_SKATING,
    comparison_key,
)
from skating_system.workbook.validation import validate_workbook


IDENTITY_NAMESPACE = UUID("ee18de08-2793-46e2-8659-aa083bc08886")


@dataclass(frozen=True)
class ComputedCompetition:
    competition: Competition
    entry_labels: dict[UUID, str]
    entry_numbers: dict[UUID, str]
    judge_labels: dict[UUID, str]
    raw_marks_by_entry: dict[UUID, tuple[object, ...]]
    result: SolveResult | CallbackResult


@dataclass(frozen=True)
class ComputeResult:
    event_name: str
    competitions: tuple[ComputedCompetition, ...]
    findings: tuple[Finding, ...]

    @property
    def has_errors(self) -> bool:
        return any(item.severity is Severity.ERROR for item in self.findings)


def compute_workbook(
    path: Path,
    competition_name: str | None = None,
) -> ComputeResult:
    validation = validate_workbook(path)
    relevant_validation = _relevant_findings(validation.findings, competition_name)
    if any(item.severity is Severity.ERROR for item in relevant_validation):
        return ComputeResult(
            event_name="", competitions=(), findings=relevant_validation
        )

    read_result = read_workbook(path)
    relevant_read = _relevant_findings(read_result.findings, competition_name)
    if read_result.data is None or any(
        item.severity is Severity.ERROR for item in relevant_read
    ):
        return ComputeResult(event_name="", competitions=(), findings=relevant_read)

    selected, selection_findings = _select_competitions(
        read_result.data, competition_name
    )
    if selection_findings:
        return ComputeResult(
            event_name=read_result.data.metadata.event_name,
            competitions=(),
            findings=tuple(selection_findings),
        )

    computed: list[ComputedCompetition] = []
    findings: list[Finding] = []
    for competition in selected:
        item, errors = _compute_competition(read_result.data, competition)
        if item is not None:
            computed.append(item)
        for error in errors:
            findings.append(
                Finding(
                    Severity.ERROR,
                    error,
                    competition=competition.name,
                )
            )
    return ComputeResult(
        event_name=read_result.data.metadata.event_name,
        competitions=tuple(computed),
        findings=tuple(findings),
    )


def _select_competitions(
    data: WorkbookData,
    requested_name: str | None,
) -> tuple[list[Competition], list[Finding]]:
    if requested_name is None:
        return list(data.competitions), []
    requested_key = comparison_key(requested_name)
    matches = [
        item for item in data.competitions if comparison_key(item.name) == requested_key
    ]
    if matches:
        return matches, []
    available = ", ".join(item.name for item in data.competitions) or "none"
    return [], [
        Finding(
            Severity.ERROR,
            f'Competition "{requested_name}" was not found. Available: {available}.',
        )
    ]


def _relevant_findings(
    findings: tuple[Finding, ...], requested_name: str | None
) -> tuple[Finding, ...]:
    if requested_name is None:
        return findings
    requested_key = comparison_key(requested_name)
    return tuple(
        item
        for item in findings
        if item.competition is None or comparison_key(item.competition) == requested_key
    )


def _compute_competition(
    data: WorkbookData,
    competition: Competition,
) -> tuple[ComputedCompetition | None, list[str]]:
    key = comparison_key(competition.name)
    score_sheet = data.score_sheets[key]
    entries = [item for item in data.entries if comparison_key(item.competition) == key]
    judges = [item for item in data.judges if comparison_key(item.competition) == key]
    entry_ids = [_stable_id(competition.name, "entry", item.entry) for item in entries]
    judge_ids = [_stable_id(competition.name, "judge", item.judge) for item in judges]
    entry_labels = dict(zip(entry_ids, (item.entry for item in entries), strict=True))
    entry_numbers = dict(zip(entry_ids, (item.number for item in entries), strict=True))
    judge_labels = dict(zip(judge_ids, (item.judge for item in judges), strict=True))
    rows = {comparison_key(row.entry): row for row in score_sheet.rows}

    if competition.scoring_method == SCORING_METHOD_SKATING:
        marks = [
            RankMark(
                judge_id,
                entry_id,
                int(
                    _mark_for_judge(
                        rows[comparison_key(entry.entry)].marks, judge.judge
                    )
                ),
            )
            for entry, entry_id in zip(entries, entry_ids, strict=True)
            for judge, judge_id in zip(judges, judge_ids, strict=True)
        ]
        result, errors = compute_solve_result(
            SkatingCompetition(
                id=_stable_id(competition.name, "competition", competition.name),
                name=competition.name,
                judge_ids=judge_ids,
                entry_ids=entry_ids,
                rank_marks=marks,
            ),
            entry_labels,
        )
    elif competition.scoring_method == SCORING_METHOD_CALLBACK:
        if competition.callback_advance_count is None:
            return None, ["callback_advance_count is required."]
        callback_marks = [
            CallbackMark(
                judge_id,
                entry_id,
                _mark_for_judge(rows[comparison_key(entry.entry)].marks, judge.judge),
            )
            for entry, entry_id in zip(entries, entry_ids, strict=True)
            for judge, judge_id in zip(judges, judge_ids, strict=True)
        ]
        result, errors = compute_callback_result(
            entry_ids,
            judge_ids,
            callback_marks,
            CallbackPolicy(
                alternate_enabled=competition.alternate_enabled,
                advance_count=competition.callback_advance_count,
            ),
        )
    else:
        return None, [f'Unsupported scoring method "{competition.scoring_method}".']

    if result is None:
        return None, errors
    raw_marks_by_entry: dict[UUID, tuple[object, ...]] = {}
    if isinstance(result, SolveResult):
        for entry, entry_id in zip(entries, entry_ids, strict=True):
            raw_marks_by_entry[entry_id] = tuple(
                int(
                    _mark_for_judge(
                        rows[comparison_key(entry.entry)].marks, judge.judge
                    )
                )
                for judge in judges
            )
    else:
        for entry_id in entry_ids:
            raw_marks_by_entry[entry_id] = tuple(
                next(
                    mark.value
                    for mark in result.marks
                    if mark.entry_id == entry_id and mark.judge_id == judge_id
                )
                for judge_id in judge_ids
            )
    return (
        ComputedCompetition(
            competition=competition,
            entry_labels=entry_labels,
            entry_numbers=entry_numbers,
            judge_labels=judge_labels,
            raw_marks_by_entry=raw_marks_by_entry,
            result=result,
        ),
        [],
    )


def _stable_id(competition: str, kind: str, value: str) -> UUID:
    return uuid5(IDENTITY_NAMESPACE, f"{competition}\x1f{kind}\x1f{value}")


def _mark_for_judge(marks: dict[str, MarkValue], judge: str) -> object:
    for actual_judge, mark in marks.items():
        if comparison_key(actual_judge) == comparison_key(judge):
            return mark.value
    raise KeyError(judge)
