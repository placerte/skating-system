from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from skating_system.domain.models import Competition, RankMark
from skating_system.services.skating_scorer import DecisionNode, compute_solve_result
from tests.test_skating_rules_audit import OFFICIAL_EXAMPLES, OfficialExample


def _competition_from_entry_marks(
    marks_by_entry: tuple[tuple[int, ...], ...],
) -> tuple[Competition, list[UUID]]:
    judge_ids = [uuid4() for _ in marks_by_entry[0]]
    entry_ids = [uuid4() for _ in marks_by_entry]
    return (
        Competition(
            id=uuid4(),
            name="Adversarial skating matrix",
            judge_ids=judge_ids,
            entry_ids=entry_ids,
            rank_marks=[
                RankMark(judge_id, entry_ids[entry_index], rank)
                for entry_index, entry_marks in enumerate(marks_by_entry)
                for judge_id, rank in zip(judge_ids, entry_marks, strict=True)
            ],
        ),
        entry_ids,
    )


def _walk(node: DecisionNode) -> list[DecisionNode]:
    nodes = [node]
    for child in node.children:
        nodes.extend(_walk(child))
    return nodes


def test_unanimous_three_judge_panel() -> None:
    # Every judge supplies the same order, so Rule 5 alone must place each entry.
    competition, entry_ids = _competition_from_entry_marks(
        ((1, 1, 1), (2, 2, 2), (3, 3, 3))
    )

    result, errors = compute_solve_result(competition)

    assert not errors
    assert result is not None
    assert [(item.entry_id, item.final_place) for item in result.placements] == [
        (entry_ids[0], 1.0),
        (entry_ids[1], 2.0),
        (entry_ids[2], 3.0),
    ]


def test_extreme_split_nine_judge_panel() -> None:
    # Four judges rank A-B-C-D while five rank B-C-D-A. Direct counting gives
    # B, C, D, A; arithmetic rank averages would incorrectly favor A over D.
    competition, entry_ids = _competition_from_entry_marks(
        (
            (1, 1, 1, 1, 4, 4, 4, 4, 4),
            (2, 2, 2, 2, 1, 1, 1, 1, 1),
            (3, 3, 3, 3, 2, 2, 2, 2, 2),
            (4, 4, 4, 4, 3, 3, 3, 3, 3),
        )
    )

    result, errors = compute_solve_result(competition)

    assert not errors
    assert result is not None
    assert [item.entry_id for item in result.placements] == [
        entry_ids[1],
        entry_ids[2],
        entry_ids[3],
        entry_ids[0],
    ]


def test_circular_matrix_reaches_exact_tie_at_maximum_depth() -> None:
    # Each entry receives every rank exactly once. Counts and sums are therefore
    # equal at every threshold; all five entries share the mean of places 1-5.
    competition, entry_ids = _competition_from_entry_marks(
        (
            (1, 2, 3, 4, 5),
            (2, 3, 4, 5, 1),
            (3, 4, 5, 1, 2),
            (4, 5, 1, 2, 3),
            (5, 1, 2, 3, 4),
        )
    )

    result, errors = compute_solve_result(competition)

    assert not errors
    assert result is not None
    assert {item.entry_id for item in result.placements} == set(entry_ids)
    assert {item.final_place for item in result.placements} == {3.0}
    terminal_ties = [
        node
        for node in _walk(result.transcript_root)
        if node.text and node.text.startswith("Unbreakable tie")
    ]
    assert len(terminal_ties) == 1
    assert terminal_ties[0].threshold == 5
    assert "final threshold" in (terminal_ties[0].reason or "")


@pytest.mark.parametrize(
    "example",
    OFFICIAL_EXAMPLES[1:],
    ids=("greater-majority", "lower-sum", "multi-threshold"),
)
def test_audited_tie_breaks_expose_structured_decisions(
    example: OfficialExample,
) -> None:
    # Expected placements and cumulative tables were independently transcribed
    # from the published Rules 6-8 examples in test_skating_rules_audit.py.
    competition, _ = _competition_from_entry_marks(example.marks)

    result, errors = compute_solve_result(competition)

    assert not errors
    assert result is not None
    assert [item.final_place for item in result.placements] == [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
    ]
    decisions = [
        node
        for node in _walk(result.transcript_root)
        if node.threshold is not None and node.reason is not None
    ]
    assert decisions
    assert all(node.rule_applied for node in decisions)
    assert any(node.counts_by_entry for node in decisions)
    if example.rule == 7:
        assert any(node.sums_by_entry for node in decisions)


def test_even_panel_rejection_is_part_of_adversarial_contract() -> None:
    competition, _ = _competition_from_entry_marks(((1, 2), (2, 1)))

    result, errors = compute_solve_result(competition)

    assert result is None
    assert "odd number of judges" in " ".join(errors)
