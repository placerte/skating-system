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

Smart workflows:

- See `docs/ui_workflows.md` for the "Entry Member Typeahead" (autocomplete combobox)
  behavior used when building teams.

---

## Screen: Competitions (List)

Purpose:

- Create and manage competitions
- Navigate to Competition Edit screen

Layout:

- Table of competitions
- Columns: name, judges count, entries count, status, computed
  - status: e.g. "draft / partial / ready" (simple heuristic)

Actions:

- Add competition (name only)
- Edit competition (opens Competition Edit screen)
- Search

Keybindings:

- a → Add competition (name-only modal)
- e → Edit competition (opens Competition Edit screen)
- / → Search
- Esc → Back

State touched:

- Event.competitions

---

## Screen: Competition Edit

Purpose:

- Configure competition (add judges, add entries, rename)
- Enter ranks
- Compute and view results

Layout:

- Main: Rank matrix (scrollable horizontally if needed)
  - Row headers: Entry display labels (per specs)
  - Column headers: Judge first name only (to save width)
  - Cells: Rank value (integer) or empty
- Right sidebar: Results panel (fixed, always visible)
  - Ordered placements with ties
  - Average ranks displayed to 2 decimals
  - "Provisional" label
  - Hint: "Press 'c' to compute"

Keybindings:

- j → Add judge (opens typeahead picker modal)
- e → Add entry (opens typeahead picker modal)
- r → Rename competition (text prompt)
- Enter → Edit cell rank
- c → Clear cell (if focused on matrix cell)
- C (shift+c) → Compute results
- d → Remove judge/entry (if focused on matrix header row/column)
- arrows / h,j,k,l → Navigate matrix
- Esc → Back to Competitions list (auto-save)

State touched:

- Competition.name
- Competition.judge_ids
- Competition.entry_ids
- Competition.rank_marks
- Competition.results

Notes:

- Matrix scrolls horizontally if many judges
- Results sidebar stays fixed on right
- Judge columns have fixed width (truncate long names if needed)
- Empty matrix shows overlay: "Press 'j' to add judges, 'e' to add entries"
- Remove actions (d) are immediate, no confirmation
- Partial ranks allowed; compute uses entry_count + 1 for missing ranks
- Compute is manual only (press 'C'), not automatic after each edit

---

## Textual UI conventions

- Use Textual keybindings with a `Footer` for discovery
- Keep screens uncluttered; prefer modal prompts for short inputs
- Default home actions: `r` rename, `l` load, `s` save, `p/e/c` navigate
- Show status messages inline on the current screen
