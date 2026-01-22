# Specs Clarifications

This file records clarifications and decisions for specs in `docs/specs.md`.
Each entry references a Spec ID and captures the PoC-level behavior.

## Identity and numbering

### NUM-6
- Question: How do we choose the next participant number?
- Decision: Use max(existing numbers) + 1.
- Rationale: Predictable, simple for a small PoC.

### NUM-7
- Question: Should participant numbers have a minimum size?
- Decision: Yes, numbers start at 100 or higher.
- Rationale: Keeps numbers three digits for readability.

### NUM-8
- Question: Are manual participant number edits allowed?
- Decision: No, not in this PoC.
- Rationale: Keeps the flow simple and avoids duplicates.

## Entry composition

### VAL-7
- Question: Are entries with a single member allowed?
- Decision: Yes, solo entries are valid.
- Rationale: Solo competitions are common.

### VAL-8
- Question: Can an entry contain the same participant twice?
- Decision: No.
- Rationale: Avoids ambiguous membership.

### MEM-5
- Question: Are entry roles required?
- Decision: No; roles may be blank or "Other".
- Rationale: Role enforcement is out of scope for the PoC.

## Validation and input rules

### VAL-6
- Question: How strict are required fields?
- Decision: Minimal; trim whitespace and require non-empty values.
- Rationale: Keep validation light for PoC usability.
- Notes: No email validation or minimum length checks yet.

### VAL-9
- Question: What rank values are allowed?
- Decision: Ranks must be between 1 and entry_count.

### VAL-10
- Question: Are missing ranks allowed while entering data?
- Decision: Yes.
- Rationale: Judges may provide only partial rankings.

### VAL-11
- Question: How do missing ranks affect computation?
- Decision: Missing ranks are treated as entry_count + 1 for that judge.
- Rationale: Unranked entries land at the bottom for that judge, tied.


### VAL-12
- Question: What is the minimum participant number?
- Decision: Participant numbers must be >= 100.
- Rationale: Keep numbers three digits for readability.

### VAL-13
- Question: What is required before computing results?
- Decision: At least one judge and two entries.
- Rationale: Results are not meaningful otherwise.

## Computation (PoC)

### CAL-1
- Question: What placeholder computation should PoC use?
- Decision: Average rank per entry across judges; lower average is better.
- Rationale: Simple and easy to replace later.

### CAL-2
- Question: How should missing ranks be handled in computation?
- Decision: Use entry_count + 1 for missing ranks.

### CAL-3
- Question: Should computed results be marked provisional?
- Decision: Yes.
- Rationale: Full skating system engine will replace this later.

### CAL-4
- Question: Should recompute be supported after edits?
- Decision: Yes; results should refresh after rank updates.

### RES-3
- Question: How should average ranks be displayed?
- Decision: Round to two decimals.
- Rationale: Keeps the display readable for the PoC.

## Ranking outcomes

### TIE-4
- Question: Can multiple entries share the same final rank?
- Decision: Yes, ties are allowed in final results.
- Rationale: Ties are common in skating system outcomes.

### RES-4
- Question: How are ties ordered in the display?
- Decision: Order tied entries by entry display label ascending.
- Rationale: Consistent, easy-to-scan ordering.

## Search behavior

### WFP-5
- Question: How should participant search behave?
- Decision: Fuzzy, case-insensitive (fzf/LazyVim "f" style).
- Notes: Use subsequence matching with scoring that prefers contiguous matches
  and earlier matches.

### WFN-5
- Question: How should entry search behave?
- Decision: Fuzzy, case-insensitive (fzf/LazyVim "f" style).
- Notes: Use subsequence matching with scoring that prefers contiguous matches
  and earlier matches.

## UI behavior

### UI-5
- Question: Is "show obsolete" a global toggle?
- Decision: No, keep it per-screen.
- Rationale: Different screens may need different visibility.

### UI-6
- Question: What is the default for "show obsolete"?
- Decision: Off by default on every screen.
- Rationale: Obsolete items should remain hidden unless requested.

### UI-7
- Question: How should solo entries be labeled in lists?
- Decision: Use participant number + full name.
- Rationale: Solos should be identifiable by the person.

### UI-8
- Question: How should entries with a non-empty entry name be labeled?
- Decision: Display the entry name only.
- Rationale: Named groups should stand on their own.

### UI-9
- Question: How should couple entries be labeled?
- Decision: Use leader number + both first names (example: "401 Pierre & Ariane").
- Rationale: Quick ID with minimal text.

### UI-10
- Question: How do we choose which entry label rule applies?
- Decision: If entry name is non-empty, use it. Else if members == 1, use solo
  label. Else if members == 2, use couple label. Otherwise use fallback label.
- Rationale: Prioritize explicit names, then use member-based defaults.

### UI-11
- Question: What is the fallback label for bad/unknown input?
- Decision: "Unnamed entry ({member_count} members)".
- Rationale: Keeps the UI usable even with incomplete data.

### UI-12
- Question: How do we pick the leader for couple display labels?
- Decision: Use the explicitly marked leader when available; otherwise use the
  first listed member.
- Rationale: Honors explicit data but stays resilient to missing info.
- Notes: Use entry member role "Leader" as the explicit marker.

## Persistence decisions

### PST-8
- Question: How do we handle unknown JSON fields on load?
- Decision: Preserve unknown fields when possible, otherwise ignore with a
  warning.
- Rationale: Avoid data loss while keeping the PoC resilient.

### PST-9
- Question: How do we handle schema/version mismatches?
- Decision: Warn and attempt best-effort load.
- Rationale: Keeps the PoC usable with older files.
