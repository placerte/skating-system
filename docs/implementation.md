# Implementation Plan (PoC)

This document maps specs to modules and describes what belongs in each file.
It can change as the project evolves, but keep it short and practical.

Authoritative specs:

- Domain spec: `docs/specs.md`
- Clarifications: `docs/specs_details.md`
- UI intent: `docs/ui_intent.md`

## Package layout

```
src/
  skating_system/
    __init__.py
    domain/
      models.py
      validate.py
    persistence/
      repo_port.py
      json_repo.py
      schema.py
    services/
      event_service.py
      ranking_service.py
    ui/
      app.py
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
```

Notes:

- `src_legacy/` contains the legacy snapshot for reference only.
- Keep modules small and focused; prefer extra files over large ones.

## Boundaries

- `domain/*`: pure data + pure validation (no Textual, no JSON).
- `persistence/*`: file I/O + migrations only.
- `services/*`: orchestration and convenience methods for UI.
- `ui/*`: Textual widgets/screens only.

## Domain model overview

Entities and relationships:

- Event (root)
  - participants: list[Participant]
  - entries: list[Entry]
  - competitions: list[Competition]
- Entry
  - members: list[EntryMember]
- Competition
  - judge_ids: list[UUID]
  - entry_ids: list[UUID]
  - rank_marks: list[RankMark]
  - results: CompetitionResults | None

Dataclasses live in `domain/models.py`:

- Event
  - id: UUID
  - name: str
  - participants: list[Participant]
  - entries: list[Entry]
  - competitions: list[Competition]
  - created_at: datetime | None
  - updated_at: datetime | None
  - schema_version: int | None
- Participant
  - id: UUID
  - number: int
  - first_name: str
  - last_name: str
  - email: str | None
  - is_obsolete: bool
- Entry
  - id: UUID
  - name: str
  - members: list[EntryMember]
  - is_obsolete: bool
- EntryMember
  - participant_id: UUID
  - role: str | None
  - Notes: use role "Leader" to mark the leader when available.
- Competition
  - id: UUID
  - name: str
  - judge_ids: list[UUID]
  - entry_ids: list[UUID]
  - rank_marks: list[RankMark]
  - results: CompetitionResults | None
- RankMark
  - judge_id: UUID
  - entry_id: UUID
  - rank: int
  - notes: str | None
- CompetitionResults (PoC)
  - placements: list[Placement]
  - is_provisional: bool
- Placement (PoC)
  - entry_id: UUID
  - rank: int
  - average_rank: float

## Validation responsibilities

`domain/validate.py` exposes `validate_event(event) -> list[str]`.
Validation is non-throwing and returns warnings/errors for UI display.

Key checks (see `docs/specs.md`):

- Required fields are non-empty.
- Participant numbers are >= 100 and unique.
- Entries have at least one member, no duplicates.
- RankMark uniqueness and rank range.

## Persistence design

`persistence/repo_port.py` defines the `EventRepo` protocol.

`persistence/json_repo.py`:

- Loads/saves a single Event JSON file.
- Preserves unknown fields when possible.
- Emits warnings for schema mismatches but attempts best-effort load.

`persistence/schema.py`:

- Defines current schema_version.
- Handles migrations for older versions.

## Services layer

`services/event_service.py`:

- High-level CRUD operations used by the UI.
- Participant auto-numbering (max + 1, starting at 100).
- Obsolete toggles and search helpers.

`services/ranking_service.py`:

- Computes provisional results (average rank per entry).
- Applies missing rank rule (entry_count + 1).
- Produces results with ties and provisional flag.

## UI layer

`ui/app.py` wires the Textual app and routes between screens.

Screens:

- `home.py`: event overview, load/save, unsaved changes warnings.
- `participants.py`: list, add/edit, search, obsolete toggle.
- `entries.py`: list, add/edit, search, obsolete toggle.
- `competitions.py`: list, setup, enter ranking screen.
- `ranking.py`: rank matrix, compute, show results.

Modals:

- `participant_form.py`: add/edit participant.
- `entry_form.py`: add/edit entry and members.
- `competition_form.py`: add/edit competition setup.

Entry display rules (from specs):

- Named entry: display `Entry.name`.
- Solo entry: display "{number} {first} {last}".
- Couple entry: display "{leader_number} {first1} & {first2}".
- Fallback: "Unnamed entry ({member_count} members)".

## Legacy snapshot

`src_legacy/` contains the legacy package for reference only.
Do not import it from the new rewrite.
