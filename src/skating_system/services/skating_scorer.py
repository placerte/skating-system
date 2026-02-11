from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from skating_system.domain.models import Competition, Placement


@dataclass
# reference [S-260210-1.4], [S-260210-1.17]
class DecisionNode:
    text: str
    rule_applied: str
    subset_entry_ids: list[UUID]
    children: list["DecisionNode"] = field(default_factory=list)


@dataclass
class DerivedTable:
    entry_ids: list[UUID]
    judge_ids: list[UUID]
    majority_threshold: int
    counts_by_entry: dict[UUID, list[int]]
    sums_by_entry: dict[UUID, list[int]]
    majorities_by_entry: dict[UUID, list[bool]]
    cutoff_by_entry: dict[UUID, int]


@dataclass
class SolveResult:
    placements: list[Placement]
    derived_table: DerivedTable
    transcript_root: DecisionNode


@dataclass
class CellClassification:
    is_dead: bool
    is_active: bool
    is_decisive: bool


@dataclass
# reference [S-260210-1.5]
class PlaceResult:
    placed_entries: list[UUID]
    final_place: float
    cutoff_by_entry: dict[UUID, int]
    transcript_node: DecisionNode


def compute_skating_system(competition: Competition) -> list[Placement]:
    """Compute placements and return them sorted by final_place."""
    result, errors = compute_solve_result(competition)
    if errors:
        raise ValueError("; ".join(errors))
    if result is None:
        return []
    return list(result.placements)


def compute_solve_result(
    competition: Competition,
) -> tuple[SolveResult | None, list[str]]:
    entry_ids = list(competition.entry_ids)
    judge_ids = list(competition.judge_ids)
    entry_count = len(entry_ids)
    judge_count = len(judge_ids)

    errors = validate_competition_ranks(competition)
    if errors:
        return None, errors

    if entry_count == 0 or judge_count == 0:
        return None, ["Competition requires at least one judge and one entry."]

    ranks_by_judge = _build_rank_map(competition, entry_ids, judge_ids)
    majority = judge_count // 2 + 1

    placements: list[Placement] = []
    cutoff_by_entry: dict[UUID, int] = {}
    unplaced = set(entry_ids)
    current_place = 1

    root = DecisionNode(
        text="Compute placements",
        rule_applied="Rules 5-8",
        subset_entry_ids=list(entry_ids),
    )

    while unplaced:
        result = _find_place(
            unplaced,
            ranks_by_judge,
            judge_ids,
            entry_ids,
            majority,
            current_place,
            entry_count,
        )
        root.children.append(result.transcript_node)
        for entry_id in result.placed_entries:
            placements.append(
                Placement(
                    entry_id=entry_id,
                    final_place=result.final_place,
                )
            )
            cutoff_by_entry[entry_id] = result.cutoff_by_entry[entry_id]
            unplaced.remove(entry_id)

        current_place += len(result.placed_entries)

    placements.sort(key=lambda p: (p.final_place, str(p.entry_id)))
    derived_table = _build_derived_table(
        entry_ids,
        judge_ids,
        ranks_by_judge,
        majority,
        cutoff_by_entry,
    )
    return SolveResult(
        placements=placements,
        derived_table=derived_table,
        transcript_root=root,
    ), []


def validate_competition_ranks(competition: Competition) -> list[str]:
    # reference [S-260210-1.7]
    errors: list[str] = []
    entry_ids = list(competition.entry_ids)
    judge_ids = list(competition.judge_ids)
    entry_count = len(entry_ids)

    entry_set = set(entry_ids)
    judge_set = set(judge_ids)

    for mark in competition.rank_marks:
        if mark.judge_id not in judge_set:
            errors.append(f"Unknown judge id in rank marks: {mark.judge_id}.")
        if mark.entry_id not in entry_set:
            errors.append(f"Unknown entry id in rank marks: {mark.entry_id}.")
        if mark.rank < 1 or mark.rank > entry_count:
            errors.append(f"Rank {mark.rank} out of range for entry {mark.entry_id}.")

    for judge_id in judge_ids:
        seen_entries: set[UUID] = set()
        ranks: list[int] = []
        for mark in competition.rank_marks:
            if mark.judge_id != judge_id:
                continue
            if mark.entry_id in seen_entries:
                errors.append(
                    "Duplicate rank mark for judge "
                    f"{judge_id} and entry {mark.entry_id}."
                )
                continue
            if mark.entry_id not in entry_set:
                continue
            seen_entries.add(mark.entry_id)
            ranks.append(mark.rank)

        missing = [entry_id for entry_id in entry_ids if entry_id not in seen_entries]
        if missing:
            errors.append(f"Judge {judge_id} missing ranks for {len(missing)} entries.")

        if len(ranks) != len(set(ranks)):
            errors.append(f"Judge {judge_id} has duplicate ranks.")

    return errors


def classify_cell(
    *,
    count: int,
    sum_: int,
    column_index: int,
    cutoff: int,
) -> CellClassification:
    # reference [S-260210-1.1], [S-260210-1.5], [S-260210-1.6]
    is_trivial = count == 0 and sum_ == 0
    is_past_cutoff = column_index > cutoff
    is_dead = is_trivial or is_past_cutoff
    return CellClassification(
        is_dead=is_dead,
        is_active=not is_dead,
        is_decisive=column_index == cutoff,
    )


def _build_rank_map(
    competition: Competition,
    entry_ids: list[UUID],
    judge_ids: list[UUID],
) -> dict[UUID, dict[UUID, int]]:
    ranks_by_judge: dict[UUID, dict[UUID, int]] = {
        judge_id: {} for judge_id in judge_ids
    }
    for mark in competition.rank_marks:
        if mark.judge_id in ranks_by_judge:
            ranks_by_judge[mark.judge_id][mark.entry_id] = mark.rank
    for judge_id in judge_ids:
        for entry_id in entry_ids:
            if entry_id not in ranks_by_judge[judge_id]:
                raise ValueError(f"Missing rank for judge {judge_id} entry {entry_id}.")
    return ranks_by_judge


def _find_place(
    unplaced: set[UUID],
    ranks_by_judge: dict[UUID, dict[UUID, int]],
    judge_ids: list[UUID],
    entry_order: list[UUID],
    majority: int,
    current_place: int,
    entry_count: int,
) -> PlaceResult:
    """
    Find entries for the current place using Skating System Rules 5-8.
    """
    t = current_place
    ordered_unplaced = [entry_id for entry_id in entry_order if entry_id in unplaced]
    candidates_to_check: list[UUID] | None = None

    node = DecisionNode(
        text=f"Place {current_place}",
        rule_applied="Rule 5",
        subset_entry_ids=list(ordered_unplaced),
    )

    while t <= entry_count:
        entries_to_check = (
            candidates_to_check if candidates_to_check is not None else ordered_unplaced
        )
        counts = _compute_counts(set(entries_to_check), ranks_by_judge, judge_ids, t)
        candidates = [
            entry_id for entry_id in entries_to_check if counts[entry_id] >= majority
        ]

        if not candidates:
            node.children.append(
                DecisionNode(
                    text=f"No majority at t={t}",
                    rule_applied="Rule 5",
                    subset_entry_ids=list(entries_to_check),
                )
            )
            t += 1
            if candidates_to_check is not None:
                candidates_to_check = None
            continue

        if len(candidates) == 1:
            entry_id = candidates[0]
            node.children.append(
                DecisionNode(
                    text=f"Majority at t={t}",
                    rule_applied="Rule 5",
                    subset_entry_ids=[entry_id],
                )
            )
            return PlaceResult(
                placed_entries=[entry_id],
                final_place=float(current_place),
                cutoff_by_entry={entry_id: t},
                transcript_node=node,
            )

        tie_node = DecisionNode(
            text=f"Majority tie at t={t}",
            rule_applied="Rule 6",
            subset_entry_ids=list(candidates),
        )
        winners, tie_children = _resolve_majority_tie(
            candidates, ranks_by_judge, judge_ids, t
        )
        tie_node.children.extend(tie_children)
        node.children.append(tie_node)

        if len(winners) == 1:
            entry_id = winners[0]
            return PlaceResult(
                placed_entries=[entry_id],
                final_place=float(current_place),
                cutoff_by_entry={entry_id: t},
                transcript_node=node,
            )

        if t == entry_count:
            shared_place = sum(
                range(current_place, current_place + len(winners))
            ) / len(winners)
            node.children.append(
                DecisionNode(
                    text=f"Unbreakable tie at t={t}; shared place={shared_place}",
                    rule_applied="Rule 8",
                    subset_entry_ids=list(winners),
                )
            )
            return PlaceResult(
                placed_entries=list(winners),
                final_place=shared_place,
                cutoff_by_entry={entry_id: t for entry_id in winners},
                transcript_node=node,
            )

        node.children.append(
            DecisionNode(
                text=f"Tie persists; advance to t={t + 1}",
                rule_applied="Rule 8",
                subset_entry_ids=list(winners),
            )
        )
        candidates_to_check = list(winners)
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
) -> tuple[list[UUID], list[DecisionNode]]:
    """
    Apply Rule 6 (greater count) and Rule 7 (lower sum) to resolve ties.
    Returns a list of winning entries (may still be tied after both rules)
    and transcript nodes for the tie-break steps.
    """
    nodes: list[DecisionNode] = []
    counts = _compute_counts(set(candidates), ranks_by_judge, judge_ids, t)
    max_count = max(counts[entry_id] for entry_id in candidates)
    winners = [entry_id for entry_id in candidates if counts[entry_id] == max_count]
    nodes.append(
        DecisionNode(
            text=f"Rule 6: greater count = {max_count}",
            rule_applied="Rule 6",
            subset_entry_ids=list(winners),
        )
    )

    if len(winners) == 1:
        return winners, nodes

    sums = _compute_sums(winners, ranks_by_judge, judge_ids, t)
    min_sum = min(sums[entry_id] for entry_id in winners)
    final_winners = [entry_id for entry_id in winners if sums[entry_id] == min_sum]
    nodes.append(
        DecisionNode(
            text=f"Rule 7: lower sum = {min_sum}",
            rule_applied="Rule 7",
            subset_entry_ids=list(final_winners),
        )
    )

    if len(final_winners) == 1:
        return final_winners, nodes

    nodes.append(
        DecisionNode(
            text="Still tied after Rule 7",
            rule_applied="Rule 7",
            subset_entry_ids=list(final_winners),
        )
    )
    return final_winners, nodes


def _build_derived_table(
    entry_ids: list[UUID],
    judge_ids: list[UUID],
    ranks_by_judge: dict[UUID, dict[UUID, int]],
    majority: int,
    cutoff_by_entry: dict[UUID, int],
) -> DerivedTable:
    # reference [S-260210-1.2], [S-260210-1.6]
    counts_by_entry: dict[UUID, list[int]] = {}
    sums_by_entry: dict[UUID, list[int]] = {}
    majorities_by_entry: dict[UUID, list[bool]] = {}
    entry_count = len(entry_ids)

    for entry_id in entry_ids:
        counts: list[int] = []
        sums: list[int] = []
        majors: list[bool] = []
        for t in range(1, entry_count + 1):
            count = 0
            total = 0
            for judge_id in judge_ids:
                rank = ranks_by_judge[judge_id][entry_id]
                if rank <= t:
                    count += 1
                    total += rank
            counts.append(count)
            sums.append(total)
            majors.append(count >= majority)
        counts_by_entry[entry_id] = counts
        sums_by_entry[entry_id] = sums
        majorities_by_entry[entry_id] = majors

    return DerivedTable(
        entry_ids=list(entry_ids),
        judge_ids=list(judge_ids),
        majority_threshold=majority,
        counts_by_entry=counts_by_entry,
        sums_by_entry=sums_by_entry,
        majorities_by_entry=majorities_by_entry,
        cutoff_by_entry=dict(cutoff_by_entry),
    )
