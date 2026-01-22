# UI Intent — Skating System App

This document describes user intent and interaction flow.
It is NOT an implementation document.

Domain rules are defined in: [specs.md](specs.md).

---

## Screen: Home / Event Overview

Purpose:

- Entry point of the app
- Show current event name (or “No event loaded”)
- Navigate to main sections
- Load / Save event file

Layout (rough):

- Header: Event name + current file path (if loaded)
- Menu:
  - Participants
  - Entries
  - Competitions
  - Load
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

- Event file I/O (load / save)
- Current in-memory Event (on load/new)

Notes:

- Later: show validation warnings summary somewhere on this screen
- Prefer keybindings and footer hints over button-heavy layouts
- Use modal prompts for rename/load/save actions

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
- Obsolete / unobsolete (labelled “Delete” for typical users if needed)
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

- Add and Edit share the same modal
- Validation errors stay inside the modal
- Hide obsolete by default

---

## Screen: Entries

Purpose:

- Manage entries (teams / solos)
- Manage participant roles within an entry

Layout:

- Table of entries
- Columns: name, members summary, obsolete
- Optional details pane: selected entry members + roles

Actions:

- Add
- Edit
- Obsolete / unobsolete
- Search (fuzzy)
- Toggle show obsolete

Keybindings:

- a → Add
- e → Edit
- o → Toggle obsolete
- / → Search
- t → Toggle show obsolete
- Esc → Back

State touched:

- Event.entries
- (indirectly) Event.participants via selection only

Notes:

- Entries are often created here (teams, stable groups)
- However, creating entries inline inside a Competition workflow should be supported for speed

---

## Screen: Competitions

Purpose:

- Create and manage competitions
- Enter a competition to edit ranks and view results

Layout:

- Table of competitions
- Columns (suggested): name, judges count, entries count, status, last computed
  - status: e.g. “draft / partial / ready” (simple heuristic)

Actions:

- Add competition
- Edit competition setup (name, judges, entries)
- Open ranking screen for selected competition
- Optional: duplicate competition (future convenience)
- Optional: delete = obsolete (if you ever add `is_obsolete` to competitions)

Keybindings:

- a → Add competition
- e → Edit competition setup
- Enter → Open ranking screen
- / → Search
- Esc → Back

State touched:

- Event.competitions

Notes:

- Competition setup should allow:
  - selecting judges from participants
  - selecting entries from entries
  - creating entries inline (modal) without leaving the competition workflow

---

## Screen: Competition Ranking

Purpose:

- Enter ranks
- View computed results

Layout:

- Rank matrix:
  - rows = entries
  - columns = judges
  - cell value = rank integer
- Result panel (ordered placements, ties visible)

Keybindings:

- arrows → move
- h, j, k, l → move
- Enter → edit cell
- 1 to 9 → quick edit current cell (sets rank immediately)
  - If possible: support multi-digit entry without slowing workflow (e.g. typing digits builds a number with short timeout)
- r → recompute
- Esc → back

State touched:

- Competition.rank_marks
- Competition.results (optional cache)

Notes:

- Partial input allowed
- Later: show validation warnings inline (duplicate ranks per judge, out-of-range, etc.)

---

## Textual UI conventions

- Use Textual keybindings with a `Footer` for discovery
- Keep screens uncluttered; prefer modal prompts for short inputs
- Default home actions: `r` rename, `l` load, `s` save, `p/e/c` navigate
- Show status messages inline on the current screen
