# Skating System Ranking App Specs

This document groups requirements by topic. Each requirement has a simple
ID for cross-reference in `docs/spec_tracking.md`.

## 0. Scope and intent

- GEN-1: The app ranks competitors using the Skating System (judge-based
  ordinal rankings).
- GEN-2: The app is offline-first. One Event equals one JSON file.
- GEN-3: The app should be fast to operate, resilient to messy real-world
  changes, and transparent enough to explain outcomes later.
- GEN-4: The term "rank" is used everywhere. Do not use "score" in the domain.
- GEN-5: This is a small personal PoC; optimize for clarity and usability over
  completeness or production-scale features.

Related: `docs/ui_intent.md` for flow, `docs/implementation.md` for modules.

## 1. Vocabulary

- VOC-1: Event is the container for participants and competitions.
- VOC-2: Participant is a single real person.
- VOC-3: Entry is what competes in a competition (solo, pair, team).
- VOC-4: Judge is a participant acting as a judge in a competition.
- VOC-5: Rank is an ordinal placement, with 1 as best.
- VOC-6: Result is the final ranking outcome of a competition.

## 2. Identity and lifecycle

- ID-1: All domain entities have a UUID as their true identifier.
- ID-2: Human-friendly numbers or names are not identities.
- ID-3: When an entity is recreated, it gets a new UUID.

- NUM-1: Participants have a display number for quick identification.
- NUM-2: Participant numbers are not permanent identities.
- NUM-3: If a participant is recreated, they get a new participant number.
- NUM-4: Numbers are not automatically reused.
- NUM-5: Participant numbers are unique within an event.
- NUM-6: New participants get the next available number using max + 1.
- NUM-7: Participant numbers start at 100 or higher (three digits minimum).
- NUM-8: Manual participant number edits are not allowed in this PoC.

- OBS-1: Entities are rarely deleted.
- OBS-2: Use `is_obsolete: bool` instead of deletion.
- OBS-3: Obsolete entities are hidden by default in selection lists.
- OBS-4: Obsolete entities remain in the JSON file for audit and history.
- OBS-5: UI must allow toggling "show obsolete".

- TIE-1: Ties are valid outcomes.
- TIE-2: The app must support ties conceptually.
- TIE-3: The MVP must not assume ties are impossible.
- TIE-4: Final results may contain multiple entries sharing the same rank.

## 3. Data model

### 3.1 Event

- EVT-1: Event is the persisted root object.
- EVT-2: Event fields: `id: UUID`, `name: str`.
- EVT-3: Event contains `participants: list[Participant]`.
- EVT-4: Event contains `entries: list[Entry]`.
- EVT-5: Event contains `competitions: list[Competition]`.
- EVT-6: Optional event fields: `created_at`, `updated_at`, `schema_version`.

### 3.2 Participant

- PAR-1: Participant represents a single real person.
- PAR-2: Participant fields: `id: UUID`, `number: int`, `first_name: str`,
  `last_name: str`, `email: str | None`, `is_obsolete: bool`.
- PAR-3: A participant may act as competitor via entry membership.
- PAR-4: A participant may act as judge in a competition.
- PAR-5: Judges are not a separate entity type.

### 3.3 Entry

- ENT-1: Entry represents what competes in a competition.
- ENT-2: Entry fields: `id: UUID`, `name: str`, `members: list[EntryMember]`,
  `is_obsolete: bool`.

EntryMember (internal structure):

- MEM-1: EntryMember fields: `participant_id: UUID`, `role: str`.
- MEM-2: EntryMember exists for data clarity and extensibility.
- MEM-3: EntryMember is mostly invisible in the UI.
- MEM-4: Roles are free-form strings (example: Lead, Follow, Captain).
- MEM-5: Roles are optional; use blank or "Other" when not specified.

Entry behavior:

- ENT-3: Entries can be reused across competitions in the same event.
- ENT-4: Entries can be created globally in the Entries screen.
- ENT-5: Entries can be created inline while editing a competition.

### 3.4 Competition

- COM-1: Competition represents a ranked instance within an event.
- COM-2: Competition fields: `id: UUID`, `name: str`.
- COM-3: Competition fields: `judge_ids: list[UUID]`.
- COM-4: Competition fields: `entry_ids: list[UUID]`.
- COM-5: Competition fields: `rank_marks: list[RankMark]`.
- COM-6: Optional competition fields: `results: CompetitionResults`.
- COM-7: Judges are selected from the same participant pool.
- COM-8: A participant may appear as both competitor and judge.

### 3.5 RankMark

- RM-1: RankMark represents one judge's rank for one entry.
- RM-2: RankMark fields: `judge_id: UUID`, `entry_id: UUID`, `rank: int`.
- RM-3: RankMark fields: optional `notes: str | None`.
- RM-4: One `(judge_id, entry_id)` pair has at most one RankMark.

### 3.6 CompetitionResults (optional cache)

- RES-1: Results store final placements with ties allowed.
- RES-2: Results may include a rule trace or audit log in the future.
- RES-3: Display average ranks rounded to two decimals in the PoC view.
- RES-4: When tied, order results by entry display label ascending.

## 4. Persistence and serialization

- PST-1: One Event equals one JSON file.
- PST-2: JSON fully represents the Event and all nested data.
- PST-3: JSON includes a `schema_version` or `app_version`.
- PST-4: Older versions should be migrated when feasible.
- PST-5: Serialization is full round-trip safe.
- PST-6: References are UUID-based.
- PST-7: No silent data loss.
- PST-8: Unknown fields are preserved when possible; otherwise ignore with a
  warning.
- PST-9: Schema/version mismatches warn and attempt best-effort load.

## 5. Validation behavior

- VAL-1: Validation on load produces warnings, not crashes.
- VAL-2: Detect duplicate participant numbers.
- VAL-3: Detect missing referenced IDs.
- VAL-4: Detect invalid rank values.
- VAL-5: Detect duplicate `(judge_id, entry_id)` rank marks.
- VAL-6: Required fields must be non-empty (event name, entry name,
  competition name, participant names).
- VAL-7: Entries must have at least one member.
- VAL-8: Entries must not contain duplicate participants.
- VAL-9: Rank values must be within 1..entry_count for that competition.
- VAL-10: Missing ranks are allowed during entry.
- VAL-11: When computing, missing ranks are treated as entry_count + 1 for
  that judge.
- VAL-12: Participant numbers must be >= 100.
- VAL-13: Competition results require at least one judge and two entries.

## 6. User workflows (MVP)

Event lifecycle:

- WFE-1: Create event.
- WFE-2: Save event.
- WFE-3: Open existing event.
- WFE-4: Support Save As to pick a new file path.
- WFE-5: Warn on unsaved changes before opening another file or exiting.
- WFE-6: If a file is missing or malformed, show a recoverable error and keep
  the app running.
- WFE-7: Default event file extension is `.json`.
- WFE-8: When a relative filename is provided, use the default directory
  `~/skating-events`.
- WFE-9: Remember the last loaded or saved event path and load it on startup
  when available.
- WFE-10: Use modal prompts for rename and load/save actions (keybindings).

Participants:

- WFP-1: List participants.
- WFP-2: Add or edit participants.
- WFP-3: Obsolete or unobsolete participants.
- WFP-4: Search participants.
- WFP-5: Search is case-insensitive and fuzzy (subsequence match with
  contiguous/earlier matches preferred).

Entries:

- WFN-1: Create or edit entries.
- WFN-2: Assign participants and roles.
- WFN-3: Obsolete or unobsolete entries.
- WFN-4: Search entries.
- WFN-5: Search is case-insensitive and fuzzy (subsequence match with
  contiguous/earlier matches preferred).

Competitions:

- WFC-1: Create competition.
- WFC-2: Select judges.
- WFC-3: Select or create entries inline.
- WFC-4: Enter ranks.
- WFC-5: Compute and view results.

## 7. Computation (PoC)

- CAL-1: Provide a simple provisional computation: average rank per entry
  across judges, lower average is better, ties allowed.
- CAL-2: Missing ranks use entry_count + 1 for that judge in computation.
- CAL-3: Mark computed results as provisional if the full ruleset is not
  implemented.
- CAL-4: Allow recompute when ranks change.

## 8. UI principles (non-binding)

- UI-1: Keyboard-first.
- UI-2: Fast navigation.
- UI-3: No crashes on user input.
- UI-4: Validation stays in context.
- UI-5: "Show obsolete" is a per-screen option (not global).
- UI-6: "Show obsolete" is off by default on every screen.
- UI-7: Entry display uses participant number + full name for solo entries.
- UI-8: Entries with a non-empty entry name display that name only.
- UI-9: Couple entries display leader number plus both first names
  (example: "401 Pierre & Ariane").
- UI-10: Entry label selection order: named entry first, then solo (1 member),
  then couple (2 members), then fallback label.
- UI-11: Fallback label for bad/unknown input is
  "Unnamed entry ({member_count} members)".
- UI-12: Couple display uses the explicitly marked leader when available; if
  missing, fall back to the first listed member.

## 9. Future engine

- ENG-1: Implement a published skating system ruleset.
- ENG-2: Tie handling per rulebook.
- ENG-3: Keep engine cleanly separated from UI and persistence.

## 10. Non-goals (MVP)

- NG-1: Multi-event databases.
- NG-2: Cloud sync.
- NG-3: Authentication.
- NG-4: Printing or PDF exports.
