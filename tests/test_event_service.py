from __future__ import annotations

from uuid import uuid4

from skating_system.domain.models import Entry, EntryMember, Event, Participant
from skating_system.services import event_service


def test_next_participant_number_starts_at_100() -> None:
    event = Event(id=uuid4(), name="Test Event")

    number = event_service.next_participant_number(event)

    assert number == 100


def test_next_participant_number_increments() -> None:
    event = Event(
        id=uuid4(),
        name="Test Event",
        participants=[
            Participant(id=uuid4(), number=100, first_name="A", last_name="A"),
            Participant(id=uuid4(), number=105, first_name="B", last_name="B"),
        ],
    )

    number = event_service.next_participant_number(event)

    assert number == 106


def test_entry_display_label_named_entry() -> None:
    entry = Entry(id=uuid4(), name="KaBoom!", members=[])

    label = event_service.entry_display_label(entry, {})

    assert label == "KaBoom!"


def test_entry_display_label_solo() -> None:
    participant = Participant(
        id=uuid4(), number=401, first_name="Pierre", last_name="Fox"
    )
    entry = Entry(
        id=uuid4(),
        name="",
        members=[EntryMember(participant_id=participant.id)],
    )

    label = event_service.entry_display_label(entry, {participant.id: participant})

    assert label == "401 Pierre Fox"


def test_entry_display_label_couple_leader_role() -> None:
    leader = Participant(id=uuid4(), number=401, first_name="Pierre", last_name="Fox")
    other = Participant(id=uuid4(), number=402, first_name="Ariane", last_name="Fox")
    entry = Entry(
        id=uuid4(),
        name="",
        members=[
            EntryMember(participant_id=leader.id, role="Leader"),
            EntryMember(participant_id=other.id, role="Follower"),
        ],
    )

    label = event_service.entry_display_label(
        entry,
        {leader.id: leader, other.id: other},
    )

    assert label == "401 Pierre & Ariane"


def test_fuzzy_match_score_misses() -> None:
    assert event_service.fuzzy_match_score("zz", "Pierre") is None


def test_clear_rank_mark_removes_existing_mark() -> None:
    event = Event(id=uuid4(), name="Test")
    judge = event_service.add_participant(event, first_name="J", last_name="1")
    entry_participant = event_service.add_participant(
        event, first_name="E", last_name="1"
    )
    entry = event_service.add_entry(
        event,
        name="",
        members=[EntryMember(participant_id=entry_participant.id)],
    )
    other_entry = event_service.add_entry(
        event,
        name="Other",
        members=[EntryMember(participant_id=entry_participant.id, role="Other")],
    )
    competition = event_service.add_competition(
        event,
        name="Comp",
        judge_ids=[judge.id],
        entry_ids=[entry.id, other_entry.id],
    )

    event_service.set_rank_mark(
        event,
        competition.id,
        judge_id=judge.id,
        entry_id=entry.id,
        rank=1,
    )

    removed = event_service.clear_rank_mark(
        event,
        competition.id,
        judge_id=judge.id,
        entry_id=entry.id,
    )
    assert removed is True
    assert not competition.rank_marks
