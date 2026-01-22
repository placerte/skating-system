from __future__ import annotations

from uuid import uuid4

from skating_system.domain.models import Entry, Event, Participant
from skating_system.domain.validate import validate_event


def test_validate_event_reports_basic_issues() -> None:
    participant_id = uuid4()
    entry_id = uuid4()

    event = Event(
        id=uuid4(),
        name="",
        participants=[
            Participant(
                id=participant_id,
                number=12,
                first_name="",
                last_name="",
            ),
        ],
        entries=[Entry(id=entry_id, name="", members=[])],
    )

    errors = validate_event(event)

    assert "Event name is required." in errors
    assert any("number must be >= 100" in error for error in errors)
    assert any("first/last name required" in error for error in errors)
    assert any("must have at least one member" in error for error in errors)
