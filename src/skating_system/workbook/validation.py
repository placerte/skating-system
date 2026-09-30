from __future__ import annotations

from collections import defaultdict
from collections import Counter
from pathlib import Path

from skating_system.workbook.findings import Finding, Severity, ValidationReport
from skating_system.workbook.models import (
    Competition,
    EntryAssignment,
    JudgeAssignment,
    ScoreSheet,
    WorkbookData,
)
from skating_system.workbook.reader import read_workbook
from skating_system.workbook.schema import (
    ENTRIES_SHEET,
    JUDGES_SHEET,
    SCORING_METHOD_CALLBACK,
    SCORING_METHOD_SKATING,
    SCORING_METHODS,
    comparison_key,
    normalize_text,
)

CALLBACK_ALIASES = {
    "y": "Y",
    "yes": "Y",
    "n": "N",
    "no": "N",
    "a": "A",
    "alt": "A",
    "alternate": "A",
}


# GitHub issue #3: validate workbook structure and method-specific marks.
def validate_workbook(path: Path) -> ValidationReport:
    """Read and validate a workbook, returning structured findings."""

    read_result = read_workbook(path)
    findings = list(read_result.findings)
    if read_result.data is not None:
        findings.extend(validate_data(read_result.data))
    if not any(finding.severity is Severity.ERROR for finding in findings):
        findings.append(
            Finding(
                Severity.INFO,
                "Workbook structure and marks are valid.",
            )
        )
    return ValidationReport(findings=tuple(findings))


def validate_data(data: WorkbookData) -> list[Finding]:
    """Validate parsed workbook setup associations and method-specific marks."""

    findings, competition_lookup = validate_setup_data(data)

    for key, competition in competition_lookup.items():
        score_sheet = data.score_sheets.get(key)
        if score_sheet is None:
            continue
        judges = [
            item for item in data.judges if comparison_key(item.competition) == key
        ]
        entries = [
            item for item in data.entries if comparison_key(item.competition) == key
        ]
        _validate_score_structure(competition, judges, entries, score_sheet, findings)
        if competition.scoring_method == SCORING_METHOD_SKATING:
            _validate_skating_marks(competition, judges, entries, score_sheet, findings)
        elif competition.scoring_method == SCORING_METHOD_CALLBACK:
            _validate_callback_marks(
                competition, judges, entries, score_sheet, findings
            )
    return findings


def validate_setup_data(
    data: WorkbookData,
) -> tuple[list[Finding], dict[str, Competition]]:
    """Validate setup data without requiring or validating generated sheets."""

    findings: list[Finding] = []
    competition_lookup = _validate_competitions(data.competitions, findings)
    _validate_judges(data.judges, competition_lookup, findings)
    _validate_entries(data.entries, competition_lookup, findings)
    _validate_orders(data.judges, JUDGES_SHEET, "judge", findings)
    _validate_orders(data.entries, ENTRIES_SHEET, "entry", findings)

    return findings, competition_lookup


def normalize_callback_mark(value: object) -> str | None:
    """Normalize a supported callback alias to Y, N, or A."""

    return CALLBACK_ALIASES.get(comparison_key(value))


def _validate_competitions(
    competitions: tuple[Competition, ...],
    findings: list[Finding],
) -> dict[str, Competition]:
    lookup: dict[str, Competition] = {}
    for competition in competitions:
        key = comparison_key(competition.name)
        if not key:
            continue
        if key in lookup:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'Duplicate competition name "{competition.name}".',
                    sheet="Competitions",
                    cell=f"A{competition.source_row}",
                    competition=competition.name,
                )
            )
            continue
        lookup[key] = competition
        if competition.scoring_method not in SCORING_METHODS:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{competition.name}: unsupported scoring method "{competition.scoring_method}".',
                    sheet="Competitions",
                    cell=f"B{competition.source_row}",
                    competition=competition.name,
                )
            )
        if (
            competition.scoring_method == SCORING_METHOD_CALLBACK
            and competition.callback_advance_count is None
        ):
            findings.append(
                Finding(
                    Severity.ERROR,
                    f"{competition.name}: callback_advance_count is required for callback competitions.",
                    sheet="Competitions",
                    competition=competition.name,
                )
            )
    return lookup


def _validate_judges(
    assignments: tuple[JudgeAssignment, ...],
    competitions: dict[str, Competition],
    findings: list[Finding],
) -> None:
    seen: set[tuple[str, str]] = set()
    counts: dict[str, int] = defaultdict(int)
    for assignment in assignments:
        competition_key = comparison_key(assignment.competition)
        judge_key = comparison_key(assignment.judge)
        if competition_key not in competitions:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{assignment.competition or "Judge row"}: referenced competition does not exist.',
                    sheet=JUDGES_SHEET,
                    cell=f"A{assignment.source_row}",
                    competition=assignment.competition or None,
                    judge=assignment.judge or None,
                )
            )
            continue
        counts[competition_key] += 1
        duplicate_key = (competition_key, judge_key)
        if judge_key and duplicate_key in seen:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{assignment.competition}: judge "{assignment.judge}" is assigned more than once.',
                    sheet=JUDGES_SHEET,
                    cell=f"B{assignment.source_row}",
                    competition=assignment.competition,
                    judge=assignment.judge,
                )
            )
        seen.add(duplicate_key)
    for key, competition in competitions.items():
        if counts[key] == 0:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f"{competition.name}: no judges are assigned.",
                    competition=competition.name,
                )
            )


def _validate_entries(
    assignments: tuple[EntryAssignment, ...],
    competitions: dict[str, Competition],
    findings: list[Finding],
) -> None:
    names: set[tuple[str, str]] = set()
    numbers: set[tuple[str, str]] = set()
    counts: dict[str, int] = defaultdict(int)
    for assignment in assignments:
        competition_key = comparison_key(assignment.competition)
        entry_key = comparison_key(assignment.entry)
        number_key = comparison_key(assignment.number)
        if competition_key not in competitions:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{assignment.competition or "Entry row"}: referenced competition does not exist.',
                    sheet=ENTRIES_SHEET,
                    cell=f"A{assignment.source_row}",
                    competition=assignment.competition or None,
                    entry=assignment.entry or None,
                )
            )
            continue
        counts[competition_key] += 1
        name_key = (competition_key, entry_key)
        if entry_key and name_key in names:
            findings.append(
                Finding(
                    Severity.WARNING,
                    f'{assignment.competition}: entry name "{assignment.entry}" appears more than once.',
                    sheet=ENTRIES_SHEET,
                    cell=f"B{assignment.source_row}",
                    competition=assignment.competition,
                    entry=assignment.entry,
                )
            )
        names.add(name_key)
        unique_number = (competition_key, number_key)
        if number_key and unique_number in numbers:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{assignment.competition}: entry number "{assignment.number}" appears more than once.',
                    sheet=ENTRIES_SHEET,
                    cell=f"C{assignment.source_row}",
                    competition=assignment.competition,
                    entry=assignment.entry,
                )
            )
        if number_key:
            numbers.add(unique_number)
    for key, competition in competitions.items():
        if counts[key] == 0:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f"{competition.name}: no entries are assigned.",
                    competition=competition.name,
                )
            )


def _validate_orders(
    assignments: tuple[JudgeAssignment, ...] | tuple[EntryAssignment, ...],
    sheet_name: str,
    noun: str,
    findings: list[Finding],
) -> None:
    grouped: dict[str, list[JudgeAssignment | EntryAssignment]] = defaultdict(list)
    for assignment in assignments:
        grouped[comparison_key(assignment.competition)].append(assignment)
    for group in grouped.values():
        if not group:
            continue
        orders = [assignment.order for assignment in group]
        populated = [order for order in orders if order is not None]
        competition = group[0].competition
        if populated and len(populated) != len(orders):
            findings.append(
                Finding(
                    Severity.WARNING,
                    f"{competition}: {noun} order is only partially filled; worksheet row order will be used.",
                    sheet=sheet_name,
                    competition=competition,
                )
            )
        if any(order is not None and order <= 0 for order in orders):
            findings.append(
                Finding(
                    Severity.WARNING,
                    f"{competition}: {noun} order must use positive integers; worksheet row order will be used.",
                    sheet=sheet_name,
                    competition=competition,
                )
            )
        if len(populated) != len(set(populated)):
            findings.append(
                Finding(
                    Severity.WARNING,
                    f"{competition}: duplicate {noun} order values; worksheet row order will be used.",
                    sheet=sheet_name,
                    competition=competition,
                )
            )


def _validate_score_structure(
    competition: Competition,
    judges: list[JudgeAssignment],
    entries: list[EntryAssignment],
    score_sheet: ScoreSheet,
    findings: list[Finding],
) -> None:
    expected_judges = {
        comparison_key(item.judge): item.judge for item in judges if item.judge
    }
    actual_judges = {comparison_key(judge): judge for judge in score_sheet.judges}
    judge_counts = Counter(comparison_key(judge) for judge in score_sheet.judges)
    for key, count in judge_counts.items():
        if not key:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f"{competition.name}: score sheet has a blank judge heading.",
                    sheet=score_sheet.sheet_name,
                    competition=competition.name,
                )
            )
        elif count > 1:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{competition.name}: score sheet repeats judge column "{actual_judges[key]}".',
                    sheet=score_sheet.sheet_name,
                    competition=competition.name,
                    judge=actual_judges[key],
                )
            )
    for key, judge in expected_judges.items():
        if key not in actual_judges:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{competition.name}: score sheet is missing judge column "{judge}".',
                    sheet=score_sheet.sheet_name,
                    competition=competition.name,
                    judge=judge,
                )
            )
    for key, judge in actual_judges.items():
        if key not in expected_judges:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{competition.name}: score sheet has unassigned judge column "{judge}".',
                    sheet=score_sheet.sheet_name,
                    competition=competition.name,
                    judge=judge,
                )
            )

    expected_entries = {
        (comparison_key(item.entry), comparison_key(item.number)): item
        for item in entries
    }
    actual_entries: set[tuple[str, str]] = set()
    for row in score_sheet.rows:
        key = (comparison_key(row.entry), comparison_key(row.number))
        if key in actual_entries:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{competition.name}: score sheet repeats entry "{row.entry}" number "{row.number}".',
                    sheet=score_sheet.sheet_name,
                    cell=f"A{row.source_row}",
                    competition=competition.name,
                    entry=row.entry,
                )
            )
        actual_entries.add(key)
        if key not in expected_entries:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{competition.name}: score sheet entry "{row.entry}" number "{row.number}" is not registered.',
                    sheet=score_sheet.sheet_name,
                    cell=f"A{row.source_row}",
                    competition=competition.name,
                    entry=row.entry,
                )
            )
    for key, entry in expected_entries.items():
        if key not in actual_entries:
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{competition.name}: score sheet is missing entry "{entry.entry}" number "{entry.number}".',
                    sheet=score_sheet.sheet_name,
                    competition=competition.name,
                    entry=entry.entry,
                )
            )


def _validate_skating_marks(
    competition: Competition,
    judges: list[JudgeAssignment],
    entries: list[EntryAssignment],
    score_sheet: ScoreSheet,
    findings: list[Finding],
) -> None:
    entry_count = len(entries)
    for assignment in judges:
        actual_judge = _matching_judge(assignment.judge, score_sheet.judges)
        if actual_judge is None:
            continue
        used_ranks: dict[int, tuple[str, str]] = {}
        for row in score_sheet.rows:
            mark = row.marks.get(actual_judge)
            if mark is None:
                continue
            rank = _integer_rank(mark.value)
            if rank is None:
                description = (
                    "blank" if normalize_text(mark.value) == "" else f'"{mark.value}"'
                )
                findings.append(
                    Finding(
                        Severity.ERROR,
                        f'{competition.name}: Judge "{assignment.judge}" has invalid rank {description} for entry "{row.entry}"; expected an integer from 1 to {entry_count}.',
                        sheet=score_sheet.sheet_name,
                        cell=mark.cell,
                        competition=competition.name,
                        judge=assignment.judge,
                        entry=row.entry,
                    )
                )
                continue
            if rank < 1 or rank > entry_count:
                findings.append(
                    Finding(
                        Severity.ERROR,
                        f'{competition.name}: Judge "{assignment.judge}" ranked entry "{row.entry}" as {rank}; expected 1 to {entry_count}.',
                        sheet=score_sheet.sheet_name,
                        cell=mark.cell,
                        competition=competition.name,
                        judge=assignment.judge,
                        entry=row.entry,
                    )
                )
                continue
            if rank in used_ranks:
                previous_entry, _previous_cell = used_ranks[rank]
                findings.append(
                    Finding(
                        Severity.ERROR,
                        f'{competition.name}: Judge "{assignment.judge}" ranked both entry "{previous_entry}" and entry "{row.entry}" as {rank}.',
                        sheet=score_sheet.sheet_name,
                        cell=mark.cell,
                        competition=competition.name,
                        judge=assignment.judge,
                        entry=row.entry,
                    )
                )
            else:
                used_ranks[rank] = (row.entry, mark.cell)
        if set(used_ranks) != set(range(1, entry_count + 1)):
            findings.append(
                Finding(
                    Severity.ERROR,
                    f'{competition.name}: Judge "{assignment.judge}" must use every rank from 1 to {entry_count} exactly once.',
                    sheet=score_sheet.sheet_name,
                    competition=competition.name,
                    judge=assignment.judge,
                )
            )


def _validate_callback_marks(
    competition: Competition,
    judges: list[JudgeAssignment],
    entries: list[EntryAssignment],
    score_sheet: ScoreSheet,
    findings: list[Finding],
) -> None:
    del entries
    for assignment in judges:
        actual_judge = _matching_judge(assignment.judge, score_sheet.judges)
        if actual_judge is None:
            continue
        for row in score_sheet.rows:
            mark = row.marks.get(actual_judge)
            if mark is None:
                continue
            canonical = normalize_callback_mark(mark.value)
            if canonical is None:
                description = (
                    "blank" if normalize_text(mark.value) == "" else f'"{mark.value}"'
                )
                findings.append(
                    Finding(
                        Severity.ERROR,
                        f'{competition.name}: Judge "{assignment.judge}" has invalid callback mark {description} for entry "{row.entry}"; expected Y or N'
                        + (" or A." if competition.alternate_enabled else "."),
                        sheet=score_sheet.sheet_name,
                        cell=mark.cell,
                        competition=competition.name,
                        judge=assignment.judge,
                        entry=row.entry,
                    )
                )
            elif canonical == "A" and not competition.alternate_enabled:
                findings.append(
                    Finding(
                        Severity.ERROR,
                        f'{competition.name}: Judge "{assignment.judge}" marked entry "{row.entry}" Alternate, but Alternate is disabled.',
                        sheet=score_sheet.sheet_name,
                        cell=mark.cell,
                        competition=competition.name,
                        judge=assignment.judge,
                        entry=row.entry,
                    )
                )


def _matching_judge(expected: str, actual: tuple[str, ...]) -> str | None:
    expected_key = comparison_key(expected)
    for judge in actual:
        if comparison_key(judge) == expected_key:
            return judge
    return None


def _integer_rank(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None
