from __future__ import annotations

from uuid import UUID

from skating_system.domain.models import Competition, CompetitionResults, Placement


def compute_results(competition: Competition) -> CompetitionResults:
    entry_ids = list(competition.entry_ids)
    judge_ids = list(competition.judge_ids)
    entry_count = len(entry_ids)
    judge_count = len(judge_ids)

    if entry_count == 0 or judge_count == 0:
        return CompetitionResults(placements=[], is_provisional=True)

    ranks_by_judge = _build_rank_map(competition)
    averages: dict[UUID, float] = {}
    missing_rank_value = entry_count + 1

    for entry_id in entry_ids:
        total = 0
        for judge_id in judge_ids:
            total += ranks_by_judge.get(judge_id, {}).get(entry_id, missing_rank_value)
        averages[entry_id] = total / judge_count

    placements = _build_placements(averages)
    return CompetitionResults(placements=placements, is_provisional=True)


def compute_and_store_results(competition: Competition) -> CompetitionResults:
    results = compute_results(competition)
    competition.results = results
    return results


def _build_rank_map(competition: Competition) -> dict[UUID, dict[UUID, int]]:
    ranks_by_judge: dict[UUID, dict[UUID, int]] = {}
    for mark in competition.rank_marks:
        ranks_by_judge.setdefault(mark.judge_id, {})[mark.entry_id] = mark.rank
    return ranks_by_judge


def _build_placements(averages: dict[UUID, float]) -> list[Placement]:
    sorted_entries = sorted(averages.items(), key=lambda item: (item[1], str(item[0])))
    placements: list[Placement] = []
    current_rank = 0
    last_average: float | None = None

    for index, (entry_id, average) in enumerate(sorted_entries, start=1):
        if last_average is None or average != last_average:
            current_rank = index
        placements.append(
            Placement(
                entry_id=entry_id,
                rank=current_rank,
                average_rank=average,
            )
        )
        last_average = average

    return placements
