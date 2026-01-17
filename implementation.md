# Implementation Plan (MVP)

This document maps specs → modules. It is allowed to change, but should remain small.

Authoritative documents:
- Domain spec: [specs.md](specs.md)
- UI intent: [ui_intent.md](ui_intent.md)

## Package layout

src/
  skating_system/
    __init__.py
  domain/
    models.py              # dataclasses: Event, Participant, Entry, EntryMember, Competition, RankMark
    validate.py            # validate_event(event) -> list[str]
  persistence/
    repo_port.py           # Protocol: EventRepo
    json_repo.py           # JsonEventRepo implements EventRepo
    schema.py              # schema_version + migration helpers
  services/
    event_service.py       # high-level operations used by UI
  ui/
    app.py                 # Textual App + routing between screens
    screens/
      home.py
      participants.py
      entries.py
      competitions.py
      ranking.py
    modals/
      participant_form.py
      entry_form.py
      competition_form.py

## Boundaries

- domain/*: pure data + pure validation (no Textual, no JSON)
- persistence/*: file I/O + migrations only
- services/*: orchestration and convenience methods for UI
- ui/*: Textual widgets/screens only

## Persistence decisions

- One event per JSON file
- JSON contains schema_version
- Unknown fields: ignored (early) or preserved (later)

## MVP deliverable

- Open/create event
- Participants CRUD (obsolete instead of delete)
- Entries CRUD
- Competitions CRUD (select judges/entries)
- Rank entry matrix + store RankMarks
- Results placeholder (engine not implemented yet)

