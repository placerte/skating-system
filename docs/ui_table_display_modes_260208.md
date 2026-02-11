# UI Table Display Modes — Skating System

Date: 2026-02-08

## Purpose
Lock UI-only display behavior for the skating-system table, covering:
- entry label display cycles;
- judge label display cycles;
- judge letter assignment rules;
- invariants related to layout stability.

These rules apply **only to presentation** and do not affect domain data or scoring computation.

---

## Core principle

> **Display modes modify rendered text only; they must never alter column widths, ordering, or computation results.**

The table layout remains stable while the visible labels cycle.

---

## Entry display modes

### S-260208-3.1 Entry display cycle
The table supports a cyclic display mode for entries:

1. **E1 (default)** — `"{entry_number} {entry_name}"`
2. **E2** — `"{entry_number}"`
3. **E3** — `"{entry_name}"`

Cycling through the modes updates only the rendered text in the entry column.

### S-260208-3.2 Domain invariants
- `entry_number` is part of the domain model and remains stable.
- Selection, ordering, and computation always rely on the domain entry identifier, not the rendered label.

---

## Judge display modes

### S-260208-3.3 Judge display cycle
The table supports a cyclic display mode for judges:

1. **J1 (default)** — UI letter only (e.g. `A`, `B`, `C`)
2. **J2** — UI letter + first name (e.g. `A Alice`)
3. **J3** — full name only (e.g. `Alice Tremblay`)

These modes affect header rendering only.

### S-260208-3.4 Judge letters are UI-only
- Judge letters are **not domain data**.
- Letters are assigned by the UI at render time.
- Letters may change between competitions and views.
- Letters are never persisted.

### S-260208-3.5 Judge letter assignment rule
- Judges are assigned letters sequentially: `A, B, C, …`
- Assignment order follows the **stored order** of judges in the competition data.
- The mapping exists only for the lifetime of the table view.

---

## Layout invariants

### S-260208-3.6 Width authority
- Column widths are computed once using a shared width policy.
- Display-mode toggles **must not trigger width recomputation**.
- Header text that exceeds its column width is clipped or ellipsized.

### S-260208-3.7 Shared layout state
All table layers (main headers, sub-headers, body):
- share the same column width list;
- share the same horizontal scroll offset;
- render independently but stay visually aligned.

---

## Implementation notes

### I-260208-3.1 Display-mode state
- Entry display mode and judge display mode are UI state variables.
- Cycling updates header/body rendering without rebuilding the table schema.

### I-260208-3.2 No computation coupling
- Rank computation, majority logic, and matrix styling are unaffected by display modes.
- Display modes are applied strictly after all computation steps.

---

## Tests

### T-260208-3.1 Stability under toggling
- Toggling entry or judge display modes does not change column widths.
- Horizontal scroll position remains unchanged across toggles.

### T-260208-3.2 Mapping determinism
- For a fixed competition state, judge letter assignment is deterministic.
- Re-rendering the same view produces identical letter mappings.

---

## Definition of done

### DoD-260208-3.1
All display modes cycle correctly without affecting layout or computation.

### DoD-260208-3.2
Judge letters are confirmed to be UI-only and non-persistent.

### DoD-260208-3.3
Documentation clearly distinguishes domain identifiers from UI labels.
