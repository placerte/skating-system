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
