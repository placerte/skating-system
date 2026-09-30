from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


CALLBACK_ALIASES = {
    "y": "Y",
    "yes": "Y",
    "n": "N",
    "no": "N",
    "a": "A",
    "alt": "A",
    "alternate": "A",
}


@dataclass(frozen=True)
class CallbackPolicy:
    alternate_enabled: bool
    advance_count: int
    yes_weight: float = field(default=1.0, init=False)
    alternate_weight: float = field(default=0.5, init=False)
    no_weight: float = field(default=0.0, init=False)
    ordering: tuple[str, ...] = field(
        default=("total", "yes_count", "alternate_count"), init=False
    )
    boundary_ties_advance: bool = field(default=True, init=False)


@dataclass(frozen=True)
class CallbackMark:
    judge_id: UUID
    entry_id: UUID
    value: object


@dataclass(frozen=True)
class CanonicalCallbackMark:
    judge_id: UUID
    entry_id: UUID
    value: str


@dataclass(frozen=True)
class CallbackTally:
    entry_id: UUID
    total: float
    yes_count: int
    alternate_count: int
    no_count: int

    @property
    def ordering_key(self) -> tuple[float, int, int]:
        return (self.total, self.yes_count, self.alternate_count)


@dataclass(frozen=True)
class CallbackSelection:
    ordered_tallies: tuple[CallbackTally, ...]
    advancing_entry_ids: tuple[UUID, ...]
    boundary_key: tuple[float, int, int]


@dataclass(frozen=True)
class CallbackResult:
    marks: tuple[CanonicalCallbackMark, ...]
    selection: CallbackSelection
    policy: CallbackPolicy


def normalize_callback_value(value: object) -> str | None:
    if value is None:
        return None
    return CALLBACK_ALIASES.get(str(value).strip().casefold())


def normalize_callback_marks(
    entry_ids: list[UUID],
    judge_ids: list[UUID],
    marks: list[CallbackMark],
    *,
    alternate_enabled: bool,
) -> tuple[tuple[CanonicalCallbackMark, ...] | None, list[str]]:
    errors: list[str] = []
    expected = {
        (judge_id, entry_id) for judge_id in judge_ids for entry_id in entry_ids
    }
    seen: set[tuple[UUID, UUID]] = set()
    normalized: list[CanonicalCallbackMark] = []

    for mark in marks:
        key = (mark.judge_id, mark.entry_id)
        if mark.judge_id not in judge_ids:
            errors.append(f"Unknown callback judge id: {mark.judge_id}.")
        if mark.entry_id not in entry_ids:
            errors.append(f"Unknown callback entry id: {mark.entry_id}.")
        if key in seen:
            errors.append(
                "Duplicate callback mark for judge "
                f"{mark.judge_id} and entry {mark.entry_id}."
            )
            continue
        seen.add(key)
        canonical = normalize_callback_value(mark.value)
        if canonical is None:
            description = (
                "blank"
                if mark.value is None or str(mark.value).strip() == ""
                else repr(mark.value)
            )
            errors.append(
                f"Invalid callback mark {description} for judge {mark.judge_id} "
                f"and entry {mark.entry_id}."
            )
            continue
        if canonical == "A" and not alternate_enabled:
            errors.append(
                f"Alternate is disabled for judge {mark.judge_id} and entry "
                f"{mark.entry_id}."
            )
            continue
        normalized.append(
            CanonicalCallbackMark(
                judge_id=mark.judge_id,
                entry_id=mark.entry_id,
                value=canonical,
            )
        )

    for judge_id, entry_id in expected - seen:
        errors.append(
            f"Missing callback mark for judge {judge_id} and entry {entry_id}."
        )

    if errors:
        return None, errors
    return tuple(normalized), []


def aggregate_callback_marks(
    entry_ids: list[UUID],
    marks: tuple[CanonicalCallbackMark, ...],
    policy: CallbackPolicy,
) -> tuple[CallbackTally, ...]:
    tallies: list[CallbackTally] = []
    for entry_id in entry_ids:
        values = [mark.value for mark in marks if mark.entry_id == entry_id]
        yes_count = values.count("Y")
        alternate_count = values.count("A")
        no_count = values.count("N")
        total = (
            yes_count * policy.yes_weight
            + alternate_count * policy.alternate_weight
            + no_count * policy.no_weight
        )
        tallies.append(
            CallbackTally(
                entry_id=entry_id,
                total=total,
                yes_count=yes_count,
                alternate_count=alternate_count,
                no_count=no_count,
            )
        )
    return tuple(tallies)


def select_callback_entries(
    tallies: tuple[CallbackTally, ...],
    advance_count: int,
) -> CallbackSelection:
    if advance_count < 1:
        raise ValueError("advance_count must be a positive integer.")
    if advance_count > len(tallies):
        raise ValueError("advance_count cannot exceed the number of entries.")
    ordered = tuple(sorted(tallies, key=lambda tally: tally.ordering_key, reverse=True))
    boundary_key = ordered[advance_count - 1].ordering_key
    advancing = tuple(
        tally.entry_id for tally in ordered if tally.ordering_key >= boundary_key
    )
    return CallbackSelection(
        ordered_tallies=ordered,
        advancing_entry_ids=advancing,
        boundary_key=boundary_key,
    )


def compute_callback_result(
    entry_ids: list[UUID],
    judge_ids: list[UUID],
    marks: list[CallbackMark],
    policy: CallbackPolicy,
) -> tuple[CallbackResult | None, list[str]]:
    if policy.advance_count < 1:
        return None, ["advance_count must be a positive integer."]
    if policy.advance_count > len(entry_ids):
        return None, ["advance_count cannot exceed the number of entries."]
    normalized, errors = normalize_callback_marks(
        entry_ids,
        judge_ids,
        marks,
        alternate_enabled=policy.alternate_enabled,
    )
    if errors or normalized is None:
        return None, errors
    tallies = aggregate_callback_marks(entry_ids, normalized, policy)
    selection = select_callback_entries(tallies, policy.advance_count)
    return CallbackResult(marks=normalized, selection=selection, policy=policy), []
