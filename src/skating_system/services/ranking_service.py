from __future__ import annotations

from uuid import UUID

from skating_system.domain.models import Competition
from skating_system.services.skating_scorer import SolveResult, compute_solve_result


def compute_results(
    competition: Competition,
    entry_labels: dict[UUID, str] | None = None,
) -> tuple[SolveResult | None, list[str]]:
    """
    Compute competition results using the official Skating System (Rules 5-8).

    Returns (SolveResult, errors). On validation failure, SolveResult is None.
    """
    return compute_solve_result(competition, entry_labels=entry_labels)
