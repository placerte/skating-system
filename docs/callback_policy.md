# Callback Policy

This is the owner-approved callback policy for workbook schema version 1.

## Marks and aggregation

- Yes (`Y`) contributes `1` point.
- Alternate (`A`) contributes `0.5` points when Alternate is enabled.
- No (`N`) contributes `0` points.
- Blank, unknown, or disabled Alternate marks are validation errors and block a
  final result.

The Alternate value is an event policy, not a claimed universal Lindy Hop
standard.

## Ordering and advancement

Entries are ordered by total points, then Yes count, then Alternate count. A
competition must record a positive `callback_advance_count` in its
`Competitions` row. The first configured number of entries advance. If the
boundary falls inside a tie on all three ordering values, every entry in that
tie advances, so the final number may exceed the configured count.

Reports must state the weights, ordering, configured advance count, boundary
tie behavior, and whether Alternate was enabled. This makes the outcome
reproducible from the workbook without hidden defaults.
