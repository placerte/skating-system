# UI Workflows

This document captures "smart" workflows and interaction details that are too
specific for `docs/ui_intent.md`, but should still be treated as guidance for
implementation.

## Entry Member Typeahead (Autocomplete Combobox)

Goal: build an Entry (team / solo) quickly using a modern "typeahead" picker.

Terminology:

- Typeahead: an input that filters suggestions as you type.
- Autocomplete combobox: a common UI pattern name for the same idea.

### Display format

- Each suggestion uses an explicit number prefix:
  - Format: `[{number}] {first_name} {last_name}`
  - Example: `[401] Pierre Lacerte`

### Matching rules

- If the query starts with digits:
  - Prefer exact participant number match.
  - Otherwise prefer prefix matches (e.g. `40` matches `401`).
- Otherwise:
  - Use fuzzy, case-insensitive subsequence matching against the display format.

### Keys

- Typing updates the suggestion list.
- `Enter` selects and confirms the best current match.
- `Up/Down` changes the highlighted suggestion.
- `Esc` closes the suggestion list / cancels the action.

### After selection

- The participant is added to the Entry members list.
- The input is cleared and remains focused so another member can be added.
- Duplicate members are rejected with an inline error.

### Member roles

- Roles are optional.
- `l` toggles a "Leader" role on the selected member and clears "Leader" from
  other members.
- `r` edits role for the selected member (empty clears).
- `d` removes the selected member.

## Competition Creation and Setup

Goal: create competitions quickly, then configure judges/entries in a dedicated screen.

### Two-step workflow

1. **Create** (name only):
   - `a` (Add) on the Competitions list screen opens a simple modal.
   - Enter competition name, click Create/Cancel.
   - Competition is created with empty judges/entries lists.
   - Status message: "Competition created. Use Edit to add judges/entries."

2. **Edit** (dedicated Competition Edit screen):
   - `e` (Edit) on the Competitions list opens a full-screen Competition Edit view.
   - This screen combines setup (judges/entries) AND rank entry in one place.
   - See below for detailed Competition Edit screen workflow.

### Rationale

Separating creation (name) from configuration (judges/entries/ranks) keeps the "Add"
action lightweight. Using a dedicated screen (not modal) for editing gives room for
the matrix, results sidebar, and typeahead pickers.

---

## Competition Edit Screen Workflow

Goal: configure competition and enter ranks in a single dedicated screen.

### Layout

- **Main area:** Rank matrix (horizontally scrollable if many judges)
  - Row headers: Entry display labels (per specs.md rules)
  - Column headers: Judge first name only (to save width)
  - Cells: Rank integer or empty
  - Fixed column width with truncation if names too long
- **Right sidebar:** Results panel (fixed, always visible)
  - Ordered placements with ties allowed
  - Format: "1. [401] Pierre & Ariane (avg 1.50)"
  - Label: "Results (provisional)" or "Not computed"
  - Hint: "Press 'C' to compute"

### Adding judges and entries

- **Add judge** (`j`):
  - Opens small modal with typeahead picker (same pattern as Entry member adding).
  - Suggestions: `[{number}] {first_name} {last_name}`.
  - `Enter` selects and closes modal; new judge column appears in matrix.
  - `Esc` cancels.

- **Add entry** (`e`):
  - Opens small modal with typeahead picker.
  - Suggestions: standard entry label + member numbers (digits-first matching).
  - `Enter` selects and closes modal; new entry row appears in matrix.
  - `Esc` cancels.

### Removing judges and entries

- **Remove** (`d`):
  - If focused on a matrix row/column header, removes that entry/judge immediately.
  - No confirmation (fast operation).
  - Status message shows what was removed.
  - Any rank marks for that judge/entry are also removed.

### Entering ranks

- **Edit cell** (`Enter`):
  - Opens small text prompt for the selected cell.
  - Enter rank integer (1..entry_count) or empty to clear.
  - Auto-saves after confirming.

- **Clear cell** (`c`):
  - Clears rank for the selected cell immediately.
  - Auto-saves.

### Compute results

- **Compute** (`C` / Shift+c):
  - Runs PoC average-rank computation.
  - Updates results sidebar.
  - Auto-saves.
  - Manual only (not automatic after each rank edit).

### Other actions

- **Rename** (`r`):
  - Opens text prompt to rename the competition.
  - Auto-saves.

- **Back** (`Esc`):
  - Returns to Competitions list.
  - Auto-saves before exit.

### Empty state

- When matrix has no judges or entries, show overlay text:
  - "Press 'j' to add judges, 'e' to add entries"

### Placeholders

- Empty cells: show empty string (no placeholder).
- Headers: show actual label (judge first name, entry display label).
- Before enough data: headers and cells are just empty until populated.
