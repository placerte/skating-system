# Workbook Contract v1

An event is one `.xlsx` workbook. The workbook is the editable source of truth;
generated sheets and PDFs are disposable outputs. Workbook-facing identities are
human-readable strings, not UUIDs.

## Core sheets

The four core sheets are manually maintained. Their names are exact.

### `Event`

This is a compact key/value sheet with the columns `field` and `value`.

| field | required value |
|---|---|
| `schema_version` | `1` |
| `event_name` | Nonblank display name |

Workbook-level metadata belongs here. The schema version is text so later
versions are not confused with Excel numeric formatting.

### `Competitions`

One row per competition.

| column | requirement |
|---|---|
| `competition` | Required, nonblank, unique human-readable name/key |
| `scoring_method` | Required; `callback` or `skating` |
| `alternate_enabled` | Optional; boolean, ignored for skating |
| `status` | Optional organizer-controlled text |
| `notes` | Optional organizer notes |
| `callback_advance_count` | Required positive integer for callback competitions; ignored for skating |

### `CompetitionJudges`

One row per competition/judge assignment.

| column | requirement |
|---|---|
| `competition` | Required reference to `Competitions.competition` |
| `judge` | Required nonblank human-readable name |
| `order` | Optional positive integer display/print order |

A judge name may appear in multiple competitions, but only once within the same
competition.

### `CompetitionEntries`

One row per competition/entry assignment.

| column | requirement |
|---|---|
| `competition` | Required reference to `Competitions.competition` |
| `entry` | Required nonblank competitor, couple, or team name |
| `number` | Optional display identifier; unique within the competition |
| `order` | Optional positive integer registration/call order |

Duplicate entry names within a competition produce a warning. Duplicate
nonblank entry numbers are errors. Numbers are display text, not identities;
format cells as text when leading zeroes matter.

## Normalization and comparison

- Leading and trailing whitespace is removed from headings and text values.
- Runs of whitespace are collapsed to one space.
- Column headings compare case-insensitively; spaces in headings normalize to
  underscores.
- Competition, judge, and entry duplicate/reference comparisons are
  case-insensitive after whitespace normalization.
- Displayed values retain their original letter case.
- `alternate_enabled` accepts Excel booleans and the case-insensitive text
  forms `true`, `false`, `yes`, `no`, `1`, and `0`. Writers use Excel booleans.
- Blank optional cells use the defaults described above; blank required cells
  are errors.

## Stable ordering

Worksheet row order is the fallback order. If every row within one competition
has a valid `order`, consumers sort by `order`. A partially filled, duplicate,
or invalid `order` is a validation finding; consumers retain worksheet row
order rather than guessing.

Judge order controls public report labels (`A`, `B`, `C`, ...). Entry order
controls score sheets, call sheets, and scorecards.

## Generated score-sheet names

Score sheets use `Score - <competition>`. Excel-forbidden characters
`[ ] : * ? / \\` are replaced with `-`, and names are limited to 31 characters.
Name comparisons are case-insensitive. Collisions receive stable suffixes such
as `~2` in competition worksheet order. Commands that create sheets must print
the competition-to-sheet mapping.

`skating-system build-sheets event.xlsx` creates missing sheets and safely
refreshes drifted rows or judge columns when every existing mark maps uniquely
by entry number/name and judge name. If a nonblank mark cannot be mapped, the
command stops before writing. `--rebuild` permits replacement only after an
adjacent timestamped workbook snapshot succeeds. Orphan `Score - ` sheets are
reported and left untouched for manual recovery.

## Forward compatibility

- Missing core sheets, required columns, or required metadata are errors.
- A schema version newer than the application supports is an error; the
  application must not guess how to interpret it.
- Unknown columns on known sheets are preserved and ignored with a warning.
- Unknown sheets are preserved and ignored.
- Read-only commands never rewrite the workbook.
- Writers modify only fields or generated sheets they own and preserve unknown
  content.

## Scoring-policy boundary

This contract records the scoring method, whether callback Alternate marks are
available, and the callback advancement count. Callback aggregation and tie
handling are defined in `docs/callback_policy.md`; computed results and reports
must include that policy explicitly. Skating System calculations remain in the
scoring layer.
