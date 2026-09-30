from __future__ import annotations

from uuid import uuid4

from skating_system.domain.models import Competition, RankMark
from skating_system.services.skating_scorer import compute_solve_result


def test_simple_majority():
    """
    Test 1: Simple majority.
    5 judges, 6 entries. Winner determined by majority of 1sts.
    Entry 0 gets 3 first places (majority = 3), wins place 1.
    """
    judges = [uuid4() for _ in range(5)]
    entries = [uuid4() for _ in range(6)]

    rank_marks = [
        RankMark(judges[0], entries[0], 1),
        RankMark(judges[0], entries[1], 2),
        RankMark(judges[0], entries[2], 3),
        RankMark(judges[0], entries[3], 4),
        RankMark(judges[0], entries[4], 5),
        RankMark(judges[0], entries[5], 6),
        RankMark(judges[1], entries[0], 1),
        RankMark(judges[1], entries[1], 2),
        RankMark(judges[1], entries[2], 3),
        RankMark(judges[1], entries[3], 4),
        RankMark(judges[1], entries[4], 5),
        RankMark(judges[1], entries[5], 6),
        RankMark(judges[2], entries[0], 1),
        RankMark(judges[2], entries[1], 2),
        RankMark(judges[2], entries[2], 3),
        RankMark(judges[2], entries[3], 4),
        RankMark(judges[2], entries[4], 5),
        RankMark(judges[2], entries[5], 6),
        RankMark(judges[3], entries[1], 1),
        RankMark(judges[3], entries[0], 2),
        RankMark(judges[3], entries[2], 3),
        RankMark(judges[3], entries[3], 4),
        RankMark(judges[3], entries[4], 5),
        RankMark(judges[3], entries[5], 6),
        RankMark(judges[4], entries[2], 1),
        RankMark(judges[4], entries[0], 2),
        RankMark(judges[4], entries[1], 3),
        RankMark(judges[4], entries[3], 4),
        RankMark(judges[4], entries[4], 5),
        RankMark(judges[4], entries[5], 6),
    ]

    competition = Competition(
        id=uuid4(),
        name="Test Simple Majority",
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )

    result, errors = compute_solve_result(competition)
    assert not errors
    assert result is not None
    placements = result.placements

    assert len(placements) == 6
    assert placements[0].entry_id == entries[0]
    assert placements[0].final_place == 1.0
    assert placements[1].entry_id == entries[1]
    assert placements[1].final_place == 2.0
    assert placements[2].entry_id == entries[2]
    assert placements[2].final_place == 3.0


def test_no_majority_advance_threshold():
    """
    Test 2: No majority at t=1, resolved at t=2.
    5 judges, 4 entries. Each entry gets one or two 1st places, so no clear majority.
    Entry 0 gets all ranks <= 2 (5 judges = majority), wins.
    """
    judges = [uuid4() for _ in range(5)]
    entries = [uuid4() for _ in range(4)]

    rank_marks = [
        RankMark(judges[0], entries[0], 1),
        RankMark(judges[0], entries[1], 2),
        RankMark(judges[0], entries[2], 3),
        RankMark(judges[0], entries[3], 4),
        RankMark(judges[1], entries[1], 1),
        RankMark(judges[1], entries[0], 2),
        RankMark(judges[1], entries[2], 3),
        RankMark(judges[1], entries[3], 4),
        RankMark(judges[2], entries[2], 1),
        RankMark(judges[2], entries[0], 2),
        RankMark(judges[2], entries[1], 3),
        RankMark(judges[2], entries[3], 4),
        RankMark(judges[3], entries[3], 1),
        RankMark(judges[3], entries[0], 2),
        RankMark(judges[3], entries[1], 3),
        RankMark(judges[3], entries[2], 4),
        RankMark(judges[4], entries[0], 1),
        RankMark(judges[4], entries[1], 2),
        RankMark(judges[4], entries[2], 3),
        RankMark(judges[4], entries[3], 4),
    ]

    competition = Competition(
        id=uuid4(),
        name="Test Advance Threshold",
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )

    result, errors = compute_solve_result(competition)
    assert not errors
    assert result is not None
    placements = result.placements

    assert len(placements) == 4
    assert placements[0].entry_id == entries[0]
    assert placements[0].final_place == 1.0


def test_equal_majority_sum_break():
    """
    Test 3: Equal majority, resolved by sum.
    No majority at t=1. At t=2, entries 0 and 1 both reach count=4.
    Entry 0 has lower sum and wins by Rule 7.
    """
    judges = [uuid4() for _ in range(5)]
    entries = [uuid4() for _ in range(3)]

    rank_marks = [
        RankMark(judges[0], entries[0], 1),
        RankMark(judges[0], entries[1], 2),
        RankMark(judges[0], entries[2], 3),
        RankMark(judges[1], entries[0], 2),
        RankMark(judges[1], entries[1], 1),
        RankMark(judges[1], entries[2], 3),
        RankMark(judges[2], entries[0], 2),
        RankMark(judges[2], entries[1], 3),
        RankMark(judges[2], entries[2], 1),
        RankMark(judges[3], entries[0], 3),
        RankMark(judges[3], entries[1], 2),
        RankMark(judges[3], entries[2], 1),
        RankMark(judges[4], entries[0], 1),
        RankMark(judges[4], entries[1], 2),
        RankMark(judges[4], entries[2], 3),
    ]

    competition = Competition(
        id=uuid4(),
        name="Test Equal Majority",
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )

    result, errors = compute_solve_result(competition)
    assert not errors
    assert result is not None
    placements = result.placements

    assert len(placements) == 3
    placement_map = {p.entry_id: p for p in placements}

    assert placement_map[entries[0]].final_place == 1.0


def test_unbreakable_tie_fractional():
    """
    Test 4: Unbreakable tie with fractional rank.
    3 judges, 4 entries. Entries 0 and 1 have identical rank distributions.
    They remain tied through all thresholds and share place 1.5.
    """
    judges = [uuid4() for _ in range(3)]
    entries = [uuid4() for _ in range(4)]

    rank_marks = [
        RankMark(judges[0], entries[0], 1),
        RankMark(judges[0], entries[1], 2),
        RankMark(judges[0], entries[2], 3),
        RankMark(judges[0], entries[3], 4),
        RankMark(judges[1], entries[0], 2),
        RankMark(judges[1], entries[1], 3),
        RankMark(judges[1], entries[2], 4),
        RankMark(judges[1], entries[3], 1),
        RankMark(judges[2], entries[0], 3),
        RankMark(judges[2], entries[1], 1),
        RankMark(judges[2], entries[2], 2),
        RankMark(judges[2], entries[3], 4),
    ]

    competition = Competition(
        id=uuid4(),
        name="Test Unbreakable Tie",
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )

    result, errors = compute_solve_result(competition)
    assert not errors
    assert result is not None
    placements = result.placements

    assert len(placements) == 4
    placement_map = {p.entry_id: p for p in placements}

    assert (
        placement_map[entries[0]].final_place == placement_map[entries[1]].final_place
    )
    assert placement_map[entries[0]].final_place == 1.5


def test_missing_rank_handling():
    """
    Test 5: Missing rank handling.
    Judge 0 omits entry 2; treated as N+1 (rank 4).
    Entry 2 has the worst overall placement.
    """
    judges = [uuid4() for _ in range(3)]
    entries = [uuid4() for _ in range(3)]

    rank_marks = [
        RankMark(judges[0], entries[0], 1),
        RankMark(judges[0], entries[1], 2),
        RankMark(judges[1], entries[0], 1),
        RankMark(judges[1], entries[1], 2),
        RankMark(judges[1], entries[2], 3),
        RankMark(judges[2], entries[1], 1),
        RankMark(judges[2], entries[0], 2),
        RankMark(judges[2], entries[2], 3),
    ]

    competition = Competition(
        id=uuid4(),
        name="Test Missing Rank",
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )

    result, errors = compute_solve_result(competition)

    assert result is None
    assert any("missing ranks" in error.lower() for error in errors)


def test_rule_6_greater_count():
    """
    Test Rule 6: Greater majority wins.
    5 judges, 4 entries.
    At t=1, entry 0 has 3 first places (majority = 3), entry 1 has 2.
    Entry 0 wins by Rule 6 (greater count).
    """
    judges = [uuid4() for _ in range(5)]
    entries = [uuid4() for _ in range(4)]

    rank_marks = [
        RankMark(judges[0], entries[0], 1),
        RankMark(judges[0], entries[1], 2),
        RankMark(judges[0], entries[2], 3),
        RankMark(judges[0], entries[3], 4),
        RankMark(judges[1], entries[0], 1),
        RankMark(judges[1], entries[1], 2),
        RankMark(judges[1], entries[2], 3),
        RankMark(judges[1], entries[3], 4),
        RankMark(judges[2], entries[0], 1),
        RankMark(judges[2], entries[1], 2),
        RankMark(judges[2], entries[2], 3),
        RankMark(judges[2], entries[3], 4),
        RankMark(judges[3], entries[1], 1),
        RankMark(judges[3], entries[2], 2),
        RankMark(judges[3], entries[0], 3),
        RankMark(judges[3], entries[3], 4),
        RankMark(judges[4], entries[1], 1),
        RankMark(judges[4], entries[2], 2),
        RankMark(judges[4], entries[0], 3),
        RankMark(judges[4], entries[3], 4),
    ]

    competition = Competition(
        id=uuid4(),
        name="Test Rule 6",
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )

    result, errors = compute_solve_result(competition)
    assert not errors
    assert result is not None
    placements = result.placements

    assert len(placements) == 4
    placement_map = {p.entry_id: p for p in placements}

    assert placement_map[entries[0]].final_place == 1.0


def test_complex_scenario_multiple_ties():
    """
    Complex scenario with multiple tie-breaks across different thresholds.
    7 judges, 5 entries. Entry 0 gets the most 1st places.
    """
    judges = [uuid4() for _ in range(7)]
    entries = [uuid4() for _ in range(5)]

    rank_marks = [
        RankMark(judges[0], entries[0], 1),
        RankMark(judges[0], entries[1], 2),
        RankMark(judges[0], entries[2], 3),
        RankMark(judges[0], entries[3], 4),
        RankMark(judges[0], entries[4], 5),
        RankMark(judges[1], entries[0], 1),
        RankMark(judges[1], entries[1], 2),
        RankMark(judges[1], entries[2], 3),
        RankMark(judges[1], entries[3], 4),
        RankMark(judges[1], entries[4], 5),
        RankMark(judges[2], entries[0], 1),
        RankMark(judges[2], entries[1], 2),
        RankMark(judges[2], entries[2], 3),
        RankMark(judges[2], entries[3], 4),
        RankMark(judges[2], entries[4], 5),
        RankMark(judges[3], entries[0], 1),
        RankMark(judges[3], entries[1], 2),
        RankMark(judges[3], entries[2], 3),
        RankMark(judges[3], entries[3], 4),
        RankMark(judges[3], entries[4], 5),
        RankMark(judges[4], entries[1], 1),
        RankMark(judges[4], entries[0], 2),
        RankMark(judges[4], entries[2], 3),
        RankMark(judges[4], entries[3], 4),
        RankMark(judges[4], entries[4], 5),
        RankMark(judges[5], entries[2], 1),
        RankMark(judges[5], entries[1], 2),
        RankMark(judges[5], entries[0], 3),
        RankMark(judges[5], entries[3], 4),
        RankMark(judges[5], entries[4], 5),
        RankMark(judges[6], entries[3], 1),
        RankMark(judges[6], entries[2], 2),
        RankMark(judges[6], entries[1], 3),
        RankMark(judges[6], entries[0], 4),
        RankMark(judges[6], entries[4], 5),
    ]

    competition = Competition(
        id=uuid4(),
        name="Test Complex",
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )

    result, errors = compute_solve_result(competition)
    assert not errors
    assert result is not None
    placements = result.placements

    assert len(placements) == 5
    assert all(p.final_place > 0 for p in placements)
    assert placements[0].final_place == 1.0
    assert placements[0].entry_id == entries[0]
