# Matrix styling logic (Skating System)

Date: 2026-02-08

## Purpose
Define deterministic, low-noise styling rules for the **Rank Matrix** cells shown in the app UI.

The goal is to:
- emphasize only the information that contributes to the decision;
- reduce reading noise from trivial / irrelevant cells;
- keep rules simple and testable.

---

## Definitions

### D-260208-1.1 Matrix cell value
Each matrix cell displays two numeric components:
- **Rank count**: `X` (optionally with `*` marker when the **majority condition is satisfied** at that cutoff)
- **Running sum**: `(Y)`

Canonical string form:
- `X (Y)`
- `X* (Y)` when `*` indicates the **majority condition is satisfied** at that cutoff (i.e., `X >= majority_threshold`).
  - Note: once the majority condition becomes true at some cutoff, it will typically remain true for all larger cutoffs; therefore `*` may appear in multiple columns for the same row.

Special trivial form:
- `0 (0)`

### D-260208-1.2 Column index
Matrix columns represent cutoffs in increasing order:
- `j = 1`  → `1`
- `j = 2`  → `1–2`
- `j = 3`  → `1–3`
- …

### D-260208-1.3 Decisive cutoff per row
For each entry/row, a single **decisive cutoff index** `k` exists.
- All cells with `j <= k` are part of the decision trail for that row.
- All cells with `j > k` are past-cutoff for that row.

---

## Cell categories

### S-260208-1.1 Dead cell
A cell is **dead** if **either**:
1) it is trivially `0 (0)` (i.e., `X == 0 AND Y == 0`), OR
2) it is past the row’s decisive cutoff (i.e., `j > k`).

### S-260208-1.2 Active cell
A cell is **active** if:
- `j <= k`, AND
- it is NOT trivially `0 (0)`.

(Equivalently: active = contributes to the decision trail for that row.)

### S-260208-1.3 Decisive cell
A cell is **decisive** if:
- `j == k`.

Note: a decisive cell is typically active, but the classification rules above remain the source of truth.

---

## Styling rules

### S-260208-1.4 Dead-cell styling (single rule)
All dead cells use **one uniform dim style**.
- No internal `X` vs `(Y)` contrast.
- Applies to:
  - trivial `0 (0)` cells;
  - any cell past the cutoff (`j > k`).

### S-260208-1.5 Active-cell styling (hierarchy inside one cell)
Active cells are styled with **primary vs secondary emphasis**:
- Primary: `X` (and optional `*`) is **normal / emphasized**.
  - `*` indicates the majority condition is satisfied at that cutoff.
- Secondary: `(Y)` is **slightly dimmed**.

Rationale: `X` is the main decision signal; `(Y)` is tie-break / secondary context.

### S-260208-1.6 Decisive-cell styling (mandatory highlight)
If desired, the decisive cell (`j == k`) may receive additional emphasis (e.g., bold and/or background highlight), while preserving the active-cell hierarchy.

Important:
- The `*` marker is **not** synonymous with “decisive.”
- `*` only means the **majority condition is satisfied** at that cutoff.
- Therefore, `*` may appear in **multiple columns** for the same row (e.g., all cutoffs where `X >= majority_threshold`).

If a background is used, ensure foreground remains readable (see Contrast requirements).

---

## Contrast requirements

### S-260208-1.7 Background-safe text
If any background highlight is applied (e.g., for decisive cells), do NOT rely on generic “dim” alone.
Instead, explicitly choose foreground shades that remain readable on that background:
- Primary foreground (for `X` / `*`)
- Secondary foreground (for `(Y)`)

This requirement is only relevant for cells with custom backgrounds.

---

## Implementation guidance (Textual / Rich)

### I-260208-1.1 Rendering strategy
- **Dead cells**: render as a plain string and apply a single dim cell style.
- **Active cells**: render as a Rich `Text` with two segments:
  - segment 1: `X` (+ `*` if present) using primary style
  - segment 2: ` (Y)` using secondary style

This limits mixed-style complexity to the subset of cells that matter.

### I-260208-1.2 Canonical classifier
Given:
- `count = X`
- `sum_ = Y`
- column index `j`
- decisive cutoff index `k`

Classify:
- `is_trivial = (count == 0 and sum_ == 0)`
- `is_past_cutoff = (j > k)`
- `is_dead = is_trivial or is_past_cutoff`
- `is_active = (not is_dead)`
- `is_decisive = (j == k)`

---

## Tests

### T-260208-1.1 Category classification
For a fixed row cutoff `k`, verify:
- `0 (0)` is always dead, even when `j <= k`.
- any `j > k` is dead regardless of values.
- any `j <= k` with non-trivial value is active.

### T-260208-1.2 Styling application
- dead cell → uniform dim style, no segment styling.
- active cell → primary segment normal/emphasized, secondary segment dimmed.
- decisive cell (if enabled) → additional emphasis without breaking primary/secondary hierarchy.

---

## Definition of done

### DoD-260208-1.1
Matrix rendering implements the classifier and styling rules exactly:
- dead cells uniformly dim;
- active cells show `X` vs `(Y)` contrast;
- optional decisive highlight does not reduce readability.

### DoD-260208-1.2
Snapshot tests (or equivalent) demonstrate:
- correct classification across rows with different cutoffs;
- readable display on at least one dark terminal theme.

