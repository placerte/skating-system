# Official worked-example inventory

Issue #18 reviewed the worked examples identified by
`skating-system-references-deep-research-report.md` against the executable
fixtures in `tests/test_skating_rules_audit.py`.

## Complete official matrices

The current WDSF-linked teaching document and Svenska Danssportförbundet
Version 1, 2024-09-01 contain the same four Rules 5–8 example matrices. Their
marks, cumulative counts, cumulative sums, and final placements match the
existing `OFFICIAL_EXAMPLES` fixtures exactly:

| Rule | Competitors | Existing fixture |
|---|---|---|
| 5 | 51–56 | `rule-5` |
| 6 | 61–66 | `rule-6` |
| 7 | 71–76 | `rule-7` |
| 8 | 81–86 | `rule-8` |

These are reproductions of one example family, not eight independent examples.
Duplicating the Swedish layout as a second fixture would add no new marks or
expected behavior.

## Additional official terminal outcome

The Rule 7 text also states that three inseparable competitors occupying places
3, 4, and 5 each receive the mean placement `4.0`. It does not publish a ballot
matrix for that statement. The test
`test_official_three_way_terminal_tie_outcome` therefore uses an explicitly
derived valid matrix to exercise the published outcome without presenting the
synthetic marks as source facts.

## Sources not converted into fixtures

- Dawson 1963 and DTV 1991 are mentioned through secondary analysis, but their
  worked examples were not obtained or transcribed in the research report.
- Mora 2001 formalizes the traditional system but the report does not contain a
  distinct complete single-dance matrix from it.
- WSDC Relative Placement is a related swing system; full Rules 5–8 equivalence
  was not established.

Creating expected matrices for those sources would invent evidence. They can be
added when an inspectable primary source and complete marks are available.
