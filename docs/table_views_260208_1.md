# Table views: Full computation vs UI-facing table (Skating System)

Date: 2026-02-08

## Purpose
Capture and lock the distinction between:
1) the **full computed table** required for correctness, traceability, and testing; and
2) the **UI-facing table** that is actually rendered to users.

This document formalizes *what is computed*, *what is shown*, and *why the separation exists*.

---

## Core principle

> **The app computes the full skating-system decision state, but only exposes the minimal table required for human comprehension.**

Nothing is omitted from computation.
Only presentation is reduced.

---

## Full computed table (internal model)

### F-260208-1.1 Purpose
The full table exists to:
- guarantee correctness of the skating-system algorithm;
- provide a complete decision trail;
- enable deterministic testing and debugging;
- support future UI views, exports, or explanations.

### F-260208-1.2 Columns (conceptual)
The full computed table includes the following conceptual sections:

1) **Entries**
- entry id
- entry name

2) **Judges – raw ranks**
- one column per judge (A, B, C, …)
- ordinal placements

3) **Rank counts**
For each cutoff `j`:
- `count_j` = number of judges with rank `<= j`

4) **Majority indicators**
For each cutoff `j`:
- `has_majority_j = (count_j >= majority_threshold)`

5) **Running sums**
For each cutoff `j`:
- `sum_j` = sum of ranks `<= j`

6) **Decisive cutoff**
- `k` = first cutoff where the row resolves under skating rules

7) **Rank matrix cells**
For each cutoff `j`:
- composite value: `X (Y)` where:
  - `X = count_j`
  - `Y = sum_j`
  - `*` marker if `has_majority_j` is true

8) **Final rank**
- resolved rank position for the entry

### F-260208-1.3 Notes
- Sections 3–5 are *derivative data* but are mandatory for correctness.
- Majority is a **flag**, not a decision by itself.
- The decisive cutoff `k` is derived from the full state, not from presentation.

---

## UI-facing useful table (presentation model)

### U-260208-1.1 Purpose
The UI-facing table exists to:
- allow fast visual comparison between entries;
- make the skating decision understandable at a glance;
- minimize cognitive load and visual noise;
- preserve trust without overwhelming detail.

### U-260208-1.2 Columns shown
The UI-facing table shows **only**:

1) **Entries**
- entry id
- entry name

2) **Judges – raw ranks**
- one column per judge

3) **Rank matrix**
- one column per cutoff `j`
- displayed as `X (Y)` / `X* (Y)`
- styled according to the matrix styling rules

4) **Final rank**
- final resolved rank for the entry

### U-260208-1.3 Columns not shown explicitly
The following are **not shown as standalone columns**:
- rank counts
- majority indicators
- running sums
- decisive cutoff index

They are *embedded* in the rank matrix cells and/or inferred via styling.

---

## Relationship between the two tables

### R-260208-1.1 Information preservation
- The UI table is a **projection** of the full table.
- No information required to justify the result is lost.
- Every visible matrix cell corresponds to a fully computed internal state.

### R-260208-1.2 Debug and explain modes
Because the full table exists internally:
- a debug or `--explain` mode may expose additional sections later;
- explanations can be generated without recomputation;
- test assertions can target internal columns directly.

The default UI remains minimal.

---

## Tests

### T-260208-2.1 Computation vs presentation consistency
- Verify that UI matrix cells are derived from internal computed values.
- Verify that final rank depends only on internal computation, not styling.

### T-260208-2.2 Non-regression
- Removing or altering UI columns must not affect computed outcomes.

---

## Definition of done

### DoD-260208-2.1
The app computes all sections defined in **F-260208-1.2**, regardless of UI view.

### DoD-260208-2.2
The default UI renders only the columns defined in **U-260208-1.2**, using the locked matrix styling rules.

### DoD-260208-2.3
Documentation clearly states that the UI table is a reduced view of a fully computed decision model.
