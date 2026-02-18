from __future__ import annotations

import re
from datetime import datetime, timezone
from uuid import UUID, uuid4

from skating_system.domain.models import (
    Competition,
    Entry,
    EntryMember,
    Event,
    Participant,
    RankMark,
)


def create_event(name: str) -> Event:
    now = datetime.now(timezone.utc)
    return Event(
        id=uuid4(),
        name=name.strip(),
        created_at=now,
        updated_at=now,
        schema_version=1,
    )


def next_participant_number(event: Event) -> int:
    numbers = [participant.number for participant in event.participants]
    if not numbers:
        return 100
    return max(numbers) + 1


def add_participant(
    event: Event,
    *,
    first_name: str,
    last_name: str,
    email: str | None = None,
) -> Participant:
    participant = Participant(
        id=uuid4(),
        number=next_participant_number(event),
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email.strip() if isinstance(email, str) else email,
        is_obsolete=False,
    )
    event.participants.append(participant)
    event.updated_at = datetime.now(timezone.utc)
    return participant


def update_participant(
    event: Event,
    participant_id: UUID,
    *,
    first_name: str,
    last_name: str,
    email: str | None = None,
) -> Participant | None:
    participant = find_participant(event, participant_id)
    if participant is None:
        return None
    participant.first_name = first_name.strip()
    participant.last_name = last_name.strip()
    participant.email = email.strip() if isinstance(email, str) else email
    event.updated_at = datetime.now(timezone.utc)
    return participant


def toggle_participant_obsolete(event: Event, participant_id: UUID) -> bool:
    participant = find_participant(event, participant_id)
    if participant is None:
        return False
    participant.is_obsolete = not participant.is_obsolete
    event.updated_at = datetime.now(timezone.utc)
    return True


def add_entry(
    event: Event,
    *,
    name: str,
    members: list[EntryMember],
) -> Entry:
    entry = Entry(
        id=uuid4(),
        name=name.strip(),
        members=list(members),
        is_obsolete=False,
    )
    event.entries.append(entry)
    event.updated_at = datetime.now(timezone.utc)
    return entry


def update_entry(
    event: Event,
    entry_id: UUID,
    *,
    name: str,
    members: list[EntryMember],
) -> Entry | None:
    entry = find_entry(event, entry_id)
    if entry is None:
        return None
    entry.name = name.strip()
    entry.members = list(members)
    event.updated_at = datetime.now(timezone.utc)
    return entry


def toggle_entry_obsolete(event: Event, entry_id: UUID) -> bool:
    entry = find_entry(event, entry_id)
    if entry is None:
        return False
    entry.is_obsolete = not entry.is_obsolete
    event.updated_at = datetime.now(timezone.utc)
    return True


def add_competition(
    event: Event,
    *,
    name: str,
    judge_ids: list[UUID],
    entry_ids: list[UUID],
) -> Competition:
    competition = Competition(
        id=uuid4(),
        name=name.strip(),
        judge_ids=list(judge_ids),
        entry_ids=list(entry_ids),
        rank_marks=[],
        results=None,
        is_obsolete=False,
    )
    event.competitions.append(competition)
    event.updated_at = datetime.now(timezone.utc)
    return competition


def update_competition(
    event: Event,
    competition_id: UUID,
    *,
    name: str,
    judge_ids: list[UUID],
    entry_ids: list[UUID],
) -> Competition | None:
    competition = find_competition(event, competition_id)
    if competition is None:
        return None
    competition.name = name.strip()
    competition.judge_ids = list(judge_ids)
    competition.entry_ids = list(entry_ids)
    event.updated_at = datetime.now(timezone.utc)
    return competition


def duplicate_competition(event: Event, competition_id: UUID) -> Competition | None:
    competition = find_competition(event, competition_id)
    if competition is None:
        return None

    new_competition = Competition(
        id=uuid4(),
        name=_copy_competition_name(competition.name),
        judge_ids=list(competition.judge_ids),
        entry_ids=list(competition.entry_ids),
        rank_marks=list(competition.rank_marks),
        results=competition.results,
        is_obsolete=False,
    )
    event.competitions.append(new_competition)
    event.updated_at = datetime.now(timezone.utc)
    return new_competition


def set_rank_mark(
    event: Event,
    competition_id: UUID,
    *,
    judge_id: UUID,
    entry_id: UUID,
    rank: int,
    notes: str | None = None,
) -> RankMark | None:
    competition = find_competition(event, competition_id)
    if competition is None:
        return None
    existing = _find_rank_mark(competition, judge_id, entry_id)
    if existing:
        existing.rank = rank
        existing.notes = notes
        event.updated_at = datetime.now(timezone.utc)
        return existing

    mark = RankMark(
        judge_id=judge_id,
        entry_id=entry_id,
        rank=rank,
        notes=notes,
    )
    competition.rank_marks.append(mark)
    event.updated_at = datetime.now(timezone.utc)
    return mark


def clear_rank_mark(
    event: Event,
    competition_id: UUID,
    *,
    judge_id: UUID,
    entry_id: UUID,
) -> bool:
    competition = find_competition(event, competition_id)
    if competition is None:
        return False

    for index, mark in enumerate(competition.rank_marks):
        if mark.judge_id == judge_id and mark.entry_id == entry_id:
            competition.rank_marks.pop(index)
            event.updated_at = datetime.now(timezone.utc)
            return True
    return False


def find_participant(event: Event, participant_id: UUID) -> Participant | None:
    return next(
        (
            participant
            for participant in event.participants
            if participant.id == participant_id
        ),
        None,
    )


def find_entry(event: Event, entry_id: UUID) -> Entry | None:
    return next(
        (entry for entry in event.entries if entry.id == entry_id),
        None,
    )


def find_competition(event: Event, competition_id: UUID) -> Competition | None:
    return next(
        (
            competition
            for competition in event.competitions
            if competition.id == competition_id
        ),
        None,
    )


def entry_display_label(
    entry: Entry,
    participant_lookup: dict[UUID, Participant],
) -> str:
    if entry.name.strip():
        return entry.name.strip()

    if len(entry.members) == 1:
        participant = participant_lookup.get(entry.members[0].participant_id)
        if participant:
            return (
                f"{participant.number} {participant.first_name} {participant.last_name}"
            )

    if len(entry.members) == 2:
        leader = _leader_member(entry.members)
        other = next(member for member in entry.members if member != leader)
        leader_participant = participant_lookup.get(leader.participant_id)
        other_participant = participant_lookup.get(other.participant_id)
        if leader_participant and other_participant:
            return (
                f"{leader_participant.number} {leader_participant.first_name}"
                f" & {other_participant.first_name}"
            )

    return f"Unnamed entry ({len(entry.members)} members)"


def search_participants(event: Event, query: str) -> list[Participant]:
    query = query.strip()
    if not query:
        return list(event.participants)

    scored: list[tuple[int, Participant]] = []
    for participant in event.participants:
        label = f"{participant.number} {participant.first_name} {participant.last_name}"
        score = fuzzy_match_score(query, label)
        if score is not None:
            scored.append((score, participant))

    return [participant for _, participant in sorted(scored, key=lambda item: -item[0])]


def search_entries(
    event: Event,
    query: str,
    participant_lookup: dict[UUID, Participant],
) -> list[Entry]:
    query = query.strip()
    if not query:
        return list(event.entries)

    scored: list[tuple[int, Entry]] = []
    for entry in event.entries:
        label = entry_display_label(entry, participant_lookup)
        score = fuzzy_match_score(query, label)
        if score is not None:
            scored.append((score, entry))

    return [entry for _, entry in sorted(scored, key=lambda item: -item[0])]


def fuzzy_match_score(query: str, text: str) -> int | None:
    query = query.strip().lower()
    text = text.lower()
    if not query:
        return 0

    first_index: int | None = None
    last_index = -1
    score = 0
    contiguous = 0

    for char in query:
        index = text.find(char, last_index + 1)
        if index == -1:
            return None
        if first_index is None:
            first_index = index
        if index == last_index + 1:
            contiguous += 1
            score += 4 * contiguous
        else:
            contiguous = 0
            score += 1
        last_index = index

    if first_index is not None:
        score += max(0, 20 - first_index)
        score += max(0, 10 - (last_index - first_index))

    return score


def _find_rank_mark(
    competition: Competition,
    judge_id: UUID,
    entry_id: UUID,
) -> RankMark | None:
    return next(
        (
            mark
            for mark in competition.rank_marks
            if mark.judge_id == judge_id and mark.entry_id == entry_id
        ),
        None,
    )


_COPY_SUFFIX_RE = re.compile(r"^(?P<base>.*)\s\(copy(?:\s(?P<num>\d+))?\)$")


def _copy_competition_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        cleaned = "Competition"
    match = _COPY_SUFFIX_RE.match(cleaned)
    if match:
        base = match.group("base").strip()
        num = match.group("num")
        if num is None:
            return f"{base} (copy 2)" if base else "Competition (copy 2)"
        try:
            next_num = int(num) + 1
        except ValueError:
            next_num = 2
        return f"{base} (copy {next_num})" if base else f"Competition (copy {next_num})"
    return f"{cleaned} (copy)"


def _leader_member(members: list[EntryMember]) -> EntryMember:
    for member in members:
        if member.role and member.role.strip().lower() == "leader":
            return member
    return members[0]
