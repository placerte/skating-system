# Skating System Ranking App — Specs

## 1. Purpose

A small offline app to rank competitors using the Skating System (judge-based ordinal rankings).

The app is designed to be:

- fast to operate during real events
- resilient to messy real-world situations (late changes, re-entries, corrections)
- transparent enough to explain outcomes (eventually via rule traces)

The app is **offline-first**:  
**one Event = one JSON file**.

---

## 2. Vocabulary

- **Event**: a container for participants and competitions.
- **Participant**: a singular real person.
- **Entry**: a competition entry (solo, pair, or team).
- **Judge**: a Participant acting as a judge in a Competition.
- **Rank**: an ordinal placement (1 = best).
- **Result**: the final ranking outcome of a Competition, computed from judge ranks.

> The term **rank** is used everywhere.  
> The term **score** is intentionally not used in this project.

---

## 3. Core domain rules

### 3.1 Identity rules

- All domain entities have a **UUID** as their true identifier.
- Human-friendly numbers or names are **not identities**.

### 3.2 Participant numbering

- Participants have a `number` used for display and quick identification.
- Participant numbers are **not permanent identities**.
- If a participant is recreated:
  - they get a new UUID
  - they get a new participant number
- Numbers are not automatically reused.

### 3.3 Obsolete instead of delete

Entities are rarely deleted.

Instead:

- `is_obsolete: bool`
- Obsolete entities:
  - are hidden by default in selection lists
  - remain in the JSON file for audit/history
- UI must allow toggling “show obsolete”

### 3.4 Ties

- Ties are a **valid outcome** in the skating system.
- The app must support ties conceptually.
- Exact tie-handling behavior depends on the selected rulebook.
- The MVP must **not assume ties are impossible**.

---

## 4. Data model

### 4.1 Event

The Event is the persisted root object.

Fields:

- `id: UUID`
- `name: str`
- `participants: list[Participant]`
- `entries: list[Entry]`
- `competitions: list[Competition]`
- optional: `created_at`, `updated_at`, `schema_version`

---

### 4.2 Participant

Represents a **single real person**.

Fields:

- `id: UUID`
- `number: int` (human-friendly)
- `first_name: str`
- `last_name: str`
- optional: `email: str | None`
- `is_obsolete: bool`

Notes:

- A Participant may act as:
  - a competitor (via Entry membership)
  - a judge (in a Competition)
- Judges are **not a separate entity type**.

---

### 4.3 Entry

An Entry represents what competes in a Competition (solo, pair, or team).

Fields:

- `id: UUID`
- `name: str`
- `members: list[EntryMember]`
- `is_obsolete: bool`

#### EntryMember (internal structure)

- `participant_id: UUID`
- `role: str`

Notes:

- EntryMember exists primarily for **data clarity and extensibility**.
- It is expected to be **mostly invisible in the UI**.
- Roles are free-form strings (ex: “Lead”, “Follow”, “Captain”).

Entries:

- can be reused across multiple Competitions in the same Event
- can be created either:
  - globally (Entry management screen)
  - or inline while creating/editing a Competition

---

### 4.4 Competition

A Competition represents one ranked instance within an Event.

Fields:

- `id: UUID`
- `name: str`
- `judge_ids: list[UUID]` (Participants acting as judges)
- `entry_ids: list[UUID]`
- `rank_marks: list[RankMark]`
- optional: `results: CompetitionResults`

Notes:

- Judges are selected from the same Participant pool.
- A Participant may appear both as a competitor and a judge.

---

### RankMark

Represents one judge’s rank for one Entry.

Fields:

- `judge_id: UUID`
- `entry_id: UUID`
- `rank: int`
- optional: `notes: str | None`

Notes:

- One `(judge_id, entry_id)` pair should have at most one RankMark.

---

### CompetitionResults (optional cache)

- final placements (ties allowed)
- optional rule trace / audit log (future)

---

## 5. Persistence (JSON)

### 5.1 Storage

- One Event = one JSON file
- JSON fully represents the Event and all nested data

### 5.2 Versioning

- JSON must include a `schema_version` or `app_version`
- Older versions should be migrated when feasible

### 5.3 Serialization requirements

- Full round-trip safety
- UUID-based references
- No silent data loss

### 5.4 Validation on load (warnings, not crashes)

Detect and warn:

- duplicate participant numbers
- missing referenced IDs
- invalid rank values
- duplicate `(judge, entry)` rank marks

---

## 6. User workflows (MVP)

### 6.1 Event lifecycle

- Create Event
- Save Event
- Open existing Event

### 6.2 Participants

- List
- Add / edit
- Obsolete / unobsolete
- Search

### 6.3 Entries

- Create / edit
- Assign participants + roles
- Obsolete / unobsolete
- Search

### 6.4 Competitions

- Create competition
- Select judges
- Select or create entries inline
- Enter ranks
- Compute and view results

---

## 7. UI principles (non-binding)

- keyboard-first
- fast navigation
- no crashes on user input
- validation stays in context

---

## 8. Skating System engine (future)

- Real published ruleset
- Tie handling per rulebook
- Clean separation from UI and persistence

---

## 9. Non-goals (MVP)

- multi-event databases
- cloud sync
- authentication
- printing / PDF exports
