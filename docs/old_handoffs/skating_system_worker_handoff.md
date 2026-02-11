# Skating System – Worker Handoff Spec
Version: PoC → v1.0 scoring engine  
Scope: Replace provisional “average-rank” logic with the official Skating System

---

## 1. Purpose of this handoff

Implement the **official Skating System scoring algorithm** in the worker codebase, replacing the current provisional implementation (average of ranks).

This artifact is **execution-oriented**:
- exact rules to implement
- exact inputs / outputs
- deterministic algorithm steps
- explicit test cases to write
- authoritative reference alignment

No design exploration is expected in the worker phase.

---

## 2. Authoritative references (validation sources)

Use these as ground truth; all logic below is derived from them:

- **The Skating System (11 rules)** – official explanatory PDF with worked examples  
  → Rules 5–8: single dance  
  → Rules 9–11: multi-dance overall

Secondary validation (optional cross-check):
- DanceSport scrutineering tutorials
- NDCA / USA Dance rulebooks (state use of Skating System, defer details to PDF above)

---

## 3. Current state (baseline)

- One `Competition` = one final round (single dance semantics)
- Each judge assigns a **strict rank** to each entry
- Missing ranks are currently treated as `N + 1` (keep this rule)
- Current scoring = **average of ranks** (to be removed)

---

## 4. Target scope for v1 (MANDATORY)

### Implement:
- **Single-dance Skating System** (Rules 5–8)

### Defer:
- Multi-dance “overall” logic (Rules 9–11)

---

## 5. Definitions (must match spec)

Let:
- `N` = number of entries
- `J` = number of judges
- `majority = floor(J / 2) + 1`
- `rank[judge][entry] ∈ {1..N}`  
  Missing → treat as `N + 1`

For a threshold `t` (1..N):

- `count_t(entry)` = number of judges where `rank ≤ t`
- `sum_t(entry)` = sum of those `rank` values

---

## 6. Core algorithm — Single Dance (Rules 5–8)

Final places are assigned incrementally: `place = 1 → N`.

### Step A — Find a majority

Starting with `t = place`:
- Compute `count_t` for all unplaced entries
- If **no entry has `count_t ≥ majority`**, increment `t`
- Repeat until one or more entries achieve a majority

### Step B — Resolve multiple majorities

If multiple entries have `count_t ≥ majority`:

1. **Rule 6 — greater majority wins**
   - Higher `count_t` ranks ahead

2. **Rule 7 — equal majority**
   - Compare `sum_t`; **lower sum wins**

3. **Still tied**
   - Increment `t` and repeat **only for tied entries**

4. **Unbreakable tie**
   - If still tied at `t = N`
   - Assign **shared place = arithmetic mean**
   - Example: tie for 3rd & 4th → both get `3.5`

### Step C — Finalize

- Assign the resolved place(s)
- Remove placed entries
- Increment `place`
- Repeat until all entries placed

> Note: the column `t` used for counting does not have to match the place being awarded.

---

## 7. Output contract

Return a list of:

```
Placement(
    entry_id: EntryID,
    final_place: float   # integer or fractional (e.g. 3.5)
)
```

Sorted by ascending `final_place`.

---

## 8. Required invariants (assert / validate)

- Each judge must rank each entry at most once
- No judge ties
- All ranks must be positive integers
- Missing ranks resolved as `N + 1`
- Deterministic output

---

## 9. Test cases to implement (MANDATORY)

### Test 1 — Simple majority

5 judges, 6 entries. Winner determined by majority of 1sts.

---

### Test 2 — No majority → advance threshold

No majority at `t=1` or `t=2`, resolved at `t=3`.

---

### Test 3 — Equal majority → sum break

Two entries with same `count_t` but different `sum_t`.

---

### Test 4 — Unbreakable tie → fractional rank

Tie persists through final column.

---

### Test 5 — Missing rank handling

One judge omits a rank; treated as `N+1`.

---

## 10. Forward compatibility (DO NOT IMPLEMENT YET)

### Multi-dance (Rules 9–11)

- Rule 9: sum of per-dance results
- Rule 10: tie-break by counting “Xth-or-better” placements
- Rule 11: collapse tied couples’ raw judge marks across all dances into a synthetic single dance and apply Rules 5–8

Raw judge marks **must be preserved** so Rule 11 is possible later.

---

## 11. Acceptance criteria

- All tests pass
- Results match official examples
- No averaging logic remains
- Deterministic, reproducible output

---

## 12. Non-goals

- UI changes
- Persistence refactors
- Performance optimization
- Chairman / dance-off logic

---

**End of worker handoff**

