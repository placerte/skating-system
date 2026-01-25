from __future__ import annotations

from uuid import uuid4

from skating_system.domain.models import Competition, RankMark
from skating_system.services.ranking_service import compute_results


def test_compute_results_missing_ranks_use_last_place() -> None:
    """
    Test that missing ranks are treated as N+1 in the skating system.
    With 2 entries and 2 judges, entry_a gets rank 1 from judge_a and
    missing from judge_b (treated as 3), entry_b gets all missing (treated as 3).
    """
    entry_a = uuid4()
    entry_b = uuid4()
    judge_a = uuid4()
    judge_b = uuid4()

    competition = Competition(
        id=uuid4(),
        name="Test",
        judge_ids=[judge_a, judge_b],
        entry_ids=[entry_a, entry_b],
        rank_marks=[RankMark(judge_id=judge_a, entry_id=entry_a, rank=1)],
    )

    results = compute_results(competition)

    placement_map = {p.entry_id: p for p in results.placements}

    assert placement_map[entry_a].final_place == 1.0
    assert placement_map[entry_b].final_place == 2.0
    assert len(placement_map[entry_a].rule_trace) > 0
