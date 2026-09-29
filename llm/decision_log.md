---
id: BLK-TOOLBOX-DECISION-LOG-V1
name: Decision Log
type: toolbox
scope: core
version: 1.0
status: active
revised: 2026-03-20
summary: Records decisions with context and rationale.
tags: [core, decisions]
---

# Decision Log

Records all important decisions.

---

## Entry Format

- ID
- Date
- Context
- Decision
- Rationale
- Impact

---

## Rules

- must be explicit
- no retroactive edits
- append-only

---

## Purpose

Provide traceability and prevent decision drift.

---

## Entries

### WB-001

- Date: 2026-09-28
- Context: Workbook contract v1 needs an event name and a schema version.
- Decision: Store workbook-level values in an `Event` key/value worksheet.
- Rationale: There is more than one general value, matching the owner's rule
  for choosing a general-data sheet over special cells in `Competitions`.
- Impact: Every v1 workbook requires `schema_version` and `event_name` rows in
  `Event`.

### WB-002

- Date: 2026-09-28
- Context: Human-readable entry names may legitimately repeat.
- Decision: Duplicate entry names within one competition are warnings;
  duplicate nonblank entry numbers remain errors.
- Rationale: Owner answer on GitHub issue #2.
- Impact: Validation must allow computation after an acknowledged name warning
  if no blocking errors exist.

### MIG-001

- Date: 2026-09-28
- Context: The legacy Textual snapshot tests blocked a green baseline during
  workbook redesign work.
- Decision: Decommission the Textual UI, its tests, and its runtime dependencies
  before completing the workbook workflow.
- Rationale: Owner direction after GitHub issue #2; the workbook CLI is the sole
  supported product direction and no domain or scoring module depends on UI code.
- Impact: The temporary `legacy-ui` command from issue #1 is removed. Reusable
  domain, persistence, service, and scoring code remains until its own migration
  work is complete.
