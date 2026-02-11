from __future__ import annotations

from collections import Counter
from typing import TypeVar
from uuid import UUID

from skating_system.domain.models import Competition, Entry, Event


def validate_event(event: Event) -> list[str]:
    errors: list[str] = []

    if _is_blank(event.name):
        errors.append("Event name is required.")

    participant_numbers = [participant.number for participant in event.participants]
    duplicate_numbers = _duplicates(participant_numbers)
    if duplicate_numbers:
        errors.append(
            "Duplicate participant numbers: "
            + ", ".join(str(number) for number in sorted(duplicate_numbers))
            + "."
        )

    for participant in event.participants:
        if participant.number < 100:
            errors.append(f"Participant {participant.id} number must be >= 100.")
        if _is_blank(participant.first_name) or _is_blank(participant.last_name):
            errors.append(f"Participant {participant.id} first/last name required.")

    participant_ids = {participant.id for participant in event.participants}
    entry_ids = {entry.id for entry in event.entries}

    for entry in event.entries:
        errors.extend(_validate_entry(entry, participant_ids))

    for competition in event.competitions:
        errors.extend(
            _validate_competition(
                competition,
                participant_ids=participant_ids,
                entry_ids=entry_ids,
            )
        )

    return errors


def _validate_entry(entry: Entry, participant_ids: set[UUID]) -> list[str]:
    errors: list[str] = []

    if len(entry.members) < 1:
        errors.append(f"Entry {entry.id} must have at least one member.")

    member_ids = [member.participant_id for member in entry.members]
    duplicate_members = _duplicates(member_ids)
    if duplicate_members:
        errors.append(f"Entry {entry.id} has duplicate members.")

    for member in entry.members:
        if member.participant_id not in participant_ids:
            errors.append(
                f"Entry {entry.id} references missing participant {member.participant_id}."
            )

    return errors


def _validate_competition(
    competition: Competition,
    *,
    participant_ids: set[UUID],
    entry_ids: set[UUID],
) -> list[str]:
    errors: list[str] = []

    if _is_blank(competition.name):
        errors.append(f"Competition {competition.id} name is required.")

    if len(competition.judge_ids) < 1 or len(competition.entry_ids) < 2:
        errors.append(
            f"Competition {competition.id} needs at least 1 judge and 2 entries."
        )

    for judge_id in competition.judge_ids:
        if judge_id not in participant_ids:
            errors.append(
                f"Competition {competition.id} references missing judge {judge_id}."
            )

    for entry_id in competition.entry_ids:
        if entry_id not in entry_ids:
            errors.append(
                f"Competition {competition.id} references missing entry {entry_id}."
            )

    seen_pairs: set[tuple[UUID, UUID]] = set()
    for rank_mark in competition.rank_marks:
        pair = (rank_mark.judge_id, rank_mark.entry_id)
        if pair in seen_pairs:
            errors.append(
                "Duplicate rank mark for judge "
                f"{rank_mark.judge_id} and entry {rank_mark.entry_id}."
            )
        else:
            seen_pairs.add(pair)

        if rank_mark.rank < 1 or rank_mark.rank > len(competition.entry_ids):
            errors.append(
                f"Rank {rank_mark.rank} out of range for entry {rank_mark.entry_id}."
            )

    return errors


T = TypeVar("T")


def _duplicates(values: list[T]) -> set[T]:
    counts = Counter(values)
    return {value for value, count in counts.items() if count > 1}


def _is_blank(value: str | None) -> bool:
    if value is None:
        return True
    return not value.strip()
