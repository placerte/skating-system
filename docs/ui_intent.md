# UI Intent — Skating System App

This document describes user intent and interaction flow.
It is NOT an implementation document.

Domain rules are defined in [specs.md](specs.md).

---

## Screen: Home / Event Overview

Purpose:

- Entry point of the app
- Show current event name
- Navigate to main sections

Layout (rough):

- Event name
- Menu:
  - Participants
  - Entries
  - Competitions
  - Save
  - Exit

Keybindings:

- p → Participants
- e → Entries
- c → Competitions
- l → Load
- s → Save
- q / Esc → Exit

State touched:

- Event itself (through loads and save?)

Notes:

- May later show validation warnings summary

---

## Screen: Participants

Purpose:

- Manage participants

Layout:

- Table of participants
- Columns: number, first name, last name, email, obsolete

Actions:

- Add
- Edit
- Obsolete / unobsolete (labeled as delete for typical users)
- Search (fuzzy search)
- Toggle show obsolete

Keybindings:

- a → Add
- e → Edit
- o → Toggle obsolete
- / → Search
- t → Toggle show obsolete
- Esc → Back

State touched:

- Event.participants

Notes:

- Add and Edit share same modal
- Validation errors stay inside modal
- Hide obsolete by default

---

## Screen: Entries

Purpose:

- Manage entries (teams / solos)
- Manage participant roles within an entry

State touched:

- Event.entries

Notes:

- Similar interaction model to Participants
- Entries like teams and such are expected to be often entered here, but solos or even couples makes a little more sense within a competition screen or workflow
- Entries like teams and such are expected to be often entered here, but solos or even couples makes a little more sense within a competition screen or workflow

---

## Screen: Competitions

Purpose:

- Create and manage competitions

[TO BE FILLED]

---

## Screen: Competition Ranking

Purpose:

- Enter ranks
- View computed results

Layout:

- Rank matrix: rows = entries, columns = judges
- Result panel (ordered placements, ties visible)

Keybindings:

- arrows → move; also
- h,j,k and l → move
- Enter → edit cell
- 1 to 9 -> quick edit of cell (enters the number without modal or other UI)
  - if possible extend for >9 (2 digits number), but not trading workflow speed
- r → recompute
- Esc → back

State touched:

- Competition.rank_marks
- Competition.results

Notes:

- Partial input allowed
