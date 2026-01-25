from __future__ import annotations

from uuid import UUID

from skating_system.domain.models import Competition, Placement


def compute_skating_system(competition: Competition) -> list[Placement]:
    """
    Compute final placements using the official Skating System (Rules 5-8).

    Returns placements sorted by final_place ascending.
    Each placement includes a human-readable rule trace explaining the result.
    """
    entry_ids = list(competition.entry_ids)
    judge_ids = list(competition.judge_ids)
    entry_count = len(entry_ids)
    judge_count = len(judge_ids)

    if entry_count == 0 or judge_count == 0:
        return []

    ranks_by_judge = _build_rank_map(competition, entry_count)
    majority = judge_count // 2 + 1

    placements: list[Placement] = []
    unplaced = set(entry_ids)
    current_place = 1

    while unplaced:
        result = _find_place(
            unplaced, ranks_by_judge, judge_ids, majority, current_place, entry_count
        )
        for entry_id in result.placed_entries:
            placements.append(
                Placement(
                    entry_id=entry_id,
                    final_place=result.final_place,
                    rule_trace=result.traces[entry_id],
                )
            )
            unplaced.remove(entry_id)

        current_place += len(result.placed_entries)

    placements.sort(key=lambda p: (p.final_place, str(p.entry_id)))
    return placements


def _build_rank_map(
    competition: Competition, entry_count: int
) -> dict[UUID, dict[UUID, int]]:
    """Build rank map with missing ranks treated as N+1."""
    missing_rank = entry_count + 1
    ranks_by_judge: dict[UUID, dict[UUID, int]] = {}

    for judge_id in competition.judge_ids:
        ranks_by_judge[judge_id] = {}

    for mark in competition.rank_marks:
        ranks_by_judge[mark.judge_id][mark.entry_id] = mark.rank

    for judge_id in competition.judge_ids:
        for entry_id in competition.entry_ids:
            if entry_id not in ranks_by_judge[judge_id]:
                ranks_by_judge[judge_id][entry_id] = missing_rank

    return ranks_by_judge


class PlaceResult:
    """Holds the result of placing one or more entries."""

    def __init__(self, placed_entries: list[UUID], final_place: float):
        self.placed_entries = placed_entries
        self.final_place = final_place
        self.traces: dict[UUID, str] = {}


def _find_place(
    unplaced: set[UUID],
    ranks_by_judge: dict[UUID, dict[UUID, int]],
    judge_ids: list[UUID],
    majority: int,
    current_place: int,
    entry_count: int,
) -> PlaceResult:
    """
    Find entries for the current place using Skating System Rules 5-8.

    Step A: Find a majority
    Step B: Resolve multiple majorities (Rule 6, 7, repeat)
    Step C: Assign shared place if unbreakable tie

    Note: We search up to entry_count+1 to handle missing ranks (treated as N+1).
    """
    t = current_place
    trace_log: dict[UUID, list[str]] = {entry_id: [] for entry_id in unplaced}
    candidates_to_check = None
    max_threshold = entry_count + 1

    while t <= max_threshold:
        if candidates_to_check is None:
            counts = _compute_counts(unplaced, ranks_by_judge, judge_ids, t)
            candidates = [
                entry_id for entry_id in unplaced if counts[entry_id] >= majority
            ]
        else:
            counts = _compute_counts(
                set(candidates_to_check), ranks_by_judge, judge_ids, t
            )
            candidates = [
                entry_id
                for entry_id in candidates_to_check
                if counts[entry_id] >= majority
            ]

        if not candidates:
            entries_to_log = (
                unplaced if candidates_to_check is None else candidates_to_check
            )
            for entry_id in entries_to_log:
                if entry_id in counts:
                    trace_log[entry_id].append(
                        f"No majority at t={t} (count={counts[entry_id]} < {majority})"
                    )
            t += 1
            if candidates_to_check is not None:
                candidates_to_check = None
            continue

        if len(candidates) == 1:
            entry_id = candidates[0]
            trace_log[entry_id].append(
                f"Majority at t={t}: count={counts[entry_id]} >= {majority}"
            )
            trace_log[entry_id].append(f"Placed {current_place}")
            result = PlaceResult([entry_id], float(current_place))
            result.traces[entry_id] = "; ".join(trace_log[entry_id])
            return result

        for entry_id in candidates:
            trace_log[entry_id].append(
                f"Majority at t={t}: count={counts[entry_id]} >= {majority}"
            )

        winners = _resolve_majority_tie(
            candidates, ranks_by_judge, judge_ids, t, trace_log
        )

        if len(winners) == 1:
            entry_id = winners[0]
            trace_log[entry_id].append(f"Placed {current_place}")
            result = PlaceResult([entry_id], float(current_place))
            result.traces[entry_id] = "; ".join(trace_log[entry_id])
            return result

        if t == max_threshold:
            shared_place = sum(
                range(current_place, current_place + len(winners))
            ) / len(winners)
            for entry_id in winners:
                trace_log[entry_id].append(
                    f"Unbreakable tie at t={max_threshold}; shared place={shared_place}"
                )
            result = PlaceResult(winners, shared_place)
            for entry_id in winners:
                result.traces[entry_id] = "; ".join(trace_log[entry_id])
            return result

        candidates_to_check = winners
        t += 1

    raise RuntimeError("Exhausted all thresholds without placing entries")


def _compute_counts(
    entries: set[UUID],
    ranks_by_judge: dict[UUID, dict[UUID, int]],
    judge_ids: list[UUID],
    t: int,
) -> dict[UUID, int]:
    """Compute count_t for each entry."""
    counts: dict[UUID, int] = {}
    for entry_id in entries:
        count = 0
        for judge_id in judge_ids:
            if ranks_by_judge[judge_id][entry_id] <= t:
                count += 1
        counts[entry_id] = count
    return counts


def _compute_sums(
    entries: list[UUID],
    ranks_by_judge: dict[UUID, dict[UUID, int]],
    judge_ids: list[UUID],
    t: int,
) -> dict[UUID, int]:
    """Compute sum_t for each entry."""
    sums: dict[UUID, int] = {}
    for entry_id in entries:
        total = 0
        for judge_id in judge_ids:
            rank = ranks_by_judge[judge_id][entry_id]
            if rank <= t:
                total += rank
        sums[entry_id] = total
    return sums


def _resolve_majority_tie(
    candidates: list[UUID],
    ranks_by_judge: dict[UUID, dict[UUID, int]],
    judge_ids: list[UUID],
    t: int,
    trace_log: dict[UUID, list[str]],
) -> list[UUID]:
    """
    Apply Rule 6 (greater count) and Rule 7 (lower sum) to resolve ties.
    Returns a list of winning entries (may still be tied after both rules).
    """
    counts = _compute_counts(set(candidates), ranks_by_judge, judge_ids, t)
    max_count = max(counts[entry_id] for entry_id in candidates)
    winners = [entry_id for entry_id in candidates if counts[entry_id] == max_count]

    if len(winners) < len(candidates):
        for entry_id in winners:
            trace_log[entry_id].append(
                f"Rule 6: greater count wins (count={max_count})"
            )
        for entry_id in candidates:
            if entry_id not in winners:
                trace_log[entry_id].append(
                    f"Eliminated by Rule 6 (count={counts[entry_id]} < {max_count})"
                )

    if len(winners) == 1:
        return winners

    sums = _compute_sums(winners, ranks_by_judge, judge_ids, t)
    min_sum = min(sums[entry_id] for entry_id in winners)
    final_winners = [entry_id for entry_id in winners if sums[entry_id] == min_sum]

    if len(final_winners) < len(winners):
        for entry_id in final_winners:
            trace_log[entry_id].append(f"Rule 7: lower sum wins (sum={min_sum})")
        for entry_id in winners:
            if entry_id not in final_winners:
                trace_log[entry_id].append(
                    f"Eliminated by Rule 7 (sum={sums[entry_id]} > {min_sum})"
                )

    if len(final_winners) == 1:
        return final_winners

    for entry_id in final_winners:
        trace_log[entry_id].append(
            f"Still tied after Rule 7 (count={counts[entry_id]}, sum={sums[entry_id]})"
        )

    return final_winners
