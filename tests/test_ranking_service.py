from __future__ import annotations

from uuid import uuid4

from skating_system.domain.models import Competition, RankMark
from skating_system.services.ranking_service import compute_results


def test_compute_results_missing_ranks_use_last_place() -> None:
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

    averages = {
        placement.entry_id: placement.average_rank for placement in results.placements
    }
    assert averages[entry_a] == 2.0
    assert averages[entry_b] == 3.0
