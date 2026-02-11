from __future__ import annotations

from skating_system.domain.models import Competition, CompetitionResults
from skating_system.services.skating_scorer import compute_skating_system


def compute_results(competition: Competition) -> CompetitionResults:
    """
    Compute competition results using the official Skating System (Rules 5-8).

    Returns CompetitionResults with placements sorted by final_place.
    Each placement includes a human-readable rule trace.
    """
    entry_count = len(competition.entry_ids)
    judge_count = len(competition.judge_ids)

    if entry_count == 0 or judge_count == 0:
        return CompetitionResults(placements=[], is_provisional=False)

    placements = compute_skating_system(competition)
    return CompetitionResults(placements=placements, is_provisional=False)


def compute_and_store_results(competition: Competition) -> CompetitionResults:
    """
    Compute results and store them in the competition object.
    """
    results = compute_results(competition)
    competition.results = results
    return results
