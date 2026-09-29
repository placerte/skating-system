from __future__ import annotations

from uuid import uuid4

from skating_system.domain.models import (
    Competition,
    Entry,
    Event,
    Participant,
    RankMark,
)
from skating_system.persistence.json_repo import JsonEventRepo
from skating_system.services.skating_scorer import (
    classify_cell,
    compute_solve_result,
)


def test_cutoff_correctness() -> None:
    judges = [uuid4() for _ in range(3)]
    entries = [uuid4() for _ in range(3)]

    rank_marks = [
        RankMark(judges[0], entries[0], 1),
        RankMark(judges[0], entries[1], 2),
        RankMark(judges[0], entries[2], 3),
        RankMark(judges[1], entries[0], 1),
        RankMark(judges[1], entries[1], 2),
        RankMark(judges[1], entries[2], 3),
        RankMark(judges[2], entries[1], 1),
        RankMark(judges[2], entries[0], 2),
        RankMark(judges[2], entries[2], 3),
    ]

    competition = Competition(
        id=uuid4(),
        name="Cutoff",
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )

    result, errors = compute_solve_result(competition)
    assert not errors
    assert result is not None
    cutoff = result.derived_table.cutoff_by_entry
    assert cutoff[entries[0]] == 1
    assert cutoff[entries[1]] == 2
    assert cutoff[entries[2]] == 3


def test_active_dead_classification() -> None:
    dead_trivial = classify_cell(count=0, sum_=0, column_index=1, cutoff=3)
    assert dead_trivial.is_dead is True
    assert dead_trivial.is_active is False

    dead_past_cutoff = classify_cell(count=2, sum_=3, column_index=4, cutoff=3)
    assert dead_past_cutoff.is_dead is True

    active = classify_cell(count=1, sum_=1, column_index=2, cutoff=3)
    assert active.is_active is True
    assert active.is_dead is False


def test_transcript_structure_contains_tie_break() -> None:
    judges = [uuid4() for _ in range(5)]
    entries = [uuid4() for _ in range(3)]

    rank_marks = [
        RankMark(judges[0], entries[0], 1),
        RankMark(judges[0], entries[1], 2),
        RankMark(judges[0], entries[2], 3),
        RankMark(judges[1], entries[1], 1),
        RankMark(judges[1], entries[0], 2),
        RankMark(judges[1], entries[2], 3),
        RankMark(judges[2], entries[2], 1),
        RankMark(judges[2], entries[0], 2),
        RankMark(judges[2], entries[1], 3),
        RankMark(judges[3], entries[1], 1),
        RankMark(judges[3], entries[0], 2),
        RankMark(judges[3], entries[2], 3),
        RankMark(judges[4], entries[0], 1),
        RankMark(judges[4], entries[1], 2),
        RankMark(judges[4], entries[2], 3),
    ]

    competition = Competition(
        id=uuid4(),
        name="Transcript",
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )

    result, errors = compute_solve_result(competition)
    assert not errors
    assert result is not None

    def walk(node, rules: set[str]) -> None:
        rules.add(node.rule_applied)
        for child in node.children:
            walk(child, rules)

    rules_seen: set[str] = set()
    walk(result.transcript_root, rules_seen)
    assert "Rule 6" in rules_seen


def test_persistence_saves_inputs_only(tmp_path) -> None:
    judge = Participant(id=uuid4(), number=100, first_name="J", last_name="")
    entry = Entry(id=uuid4(), name="E", members=[])
    competition = Competition(
        id=uuid4(),
        name="Comp",
        judge_ids=[judge.id],
        entry_ids=[entry.id],
        rank_marks=[RankMark(judge.id, entry.id, 1)],
    )
    event = Event(
        id=uuid4(),
        name="Event",
        participants=[judge],
        entries=[entry],
        competitions=[competition],
        schema_version=1,
    )
    repo = JsonEventRepo()
    file_path = tmp_path / "event.json"
    repo.save_event(file_path, event)

    raw = file_path.read_text(encoding="utf-8")
    assert '"results"' not in raw
