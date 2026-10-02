# Skating System --- Workbook + CLI Redesign Handoff

## 1. Purpose

Redesign the existing `skating-system` project around a simpler
competition-day workflow:

-   **One Excel workbook is the event source of truth and manual
    data-entry surface.**
-   **A small Python CLI reads and validates that workbook, computes
    results, and generates printable PDF artifacts.**
-   Preserve and carefully re-validate the existing Skating System
    scoring engine rather than assuming it is correct.
-   Remove the Textual TUI from the critical competition-day workflow.
-   Optimize for reliability, transparency, inspectability, and simple
    manual recovery.

This is a deliberate simplification. Do not rebuild a relational
database inside Excel. For this version, judges, competitors, couples,
and entries are represented primarily by **human-readable strings**.

The primary operational goal is that an organizer can prepare the event
in Excel, print the required cards/sheets, manually transcribe returned
judge sheets into Excel, run a CLI command, validate the data, compute
results, and immediately generate management/public/MC PDFs.

------------------------------------------------------------------------

# 2. Product Principles

## 2.1 Excel is the operational source of truth

The workbook is the canonical editable event record.

The CLI should not require users to maintain parallel JSON state.

Generated results may be reproducible from the workbook and therefore
should not become hidden authoritative state elsewhere.

## 2.2 Keep the workbook understandable without the application

An organizer should be able to open the workbook and understand:

-   what competitions exist;
-   which scoring method each uses;
-   which judges are assigned;
-   which competitors/entries are registered;
-   what marks/callbacks have been entered.

Avoid UUIDs and normalized relational structures unless a future
workflow proves they are necessary.

## 2.3 Human-readable strings first

For this version:

-   judge identity = string;
-   competitor/couple/entry identity = string;
-   competition identity = string or simple human-readable key/name.

Duplicate-name validation is acceptable and preferable to introducing
invisible IDs prematurely.

## 2.4 Generated artifacts should be disposable

Judge cards, call sheets, reports, and MC sheets are generated from the
workbook.

They may be deleted and regenerated at any time.

## 2.5 Transparency is a first-class requirement

A surprising result must be explainable after the fact.

The public report should expose raw judge rankings/callbacks while
anonymizing judge identities.

The management report should expose the same information with actual
judge identities and sufficient computation detail to audit the outcome.

## 2.6 Competition-day reliability beats architectural elegance

Prefer:

-   explicit Python;
-   small functions;
-   simple data structures;
-   strong validation;
-   deterministic output;
-   readable error messages;
-   minimal dependencies.

Avoid unnecessary frameworks, databases, ORMs, or abstraction layers.

------------------------------------------------------------------------

# 3. Scope

The redesign supports two competition scoring modes initially:

1.  **Callback**
    -   Yes
    -   No
    -   Alternate, optionally enabled per competition
2.  **Relative Placement / Skating System**
    -   Judges rank all entries.
    -   Existing Rules 5--8 engine is retained as a starting point.
    -   The implementation MUST be independently reviewed and
        regression-tested before it is trusted for a live event.

The application must also generate operational documents before scoring
and reporting documents after scoring.

------------------------------------------------------------------------

# 4. Workbook Model

Use **one `.xlsx` workbook per event**.

The workbook should remain the only manually maintained data file.

A recommended filename is:

`<event-name>.xlsx`

Example:

`retro-boreal-2027.xlsx`

Before any command that performs potentially destructive workbook
restructuring, encourage or automatically create a timestamped snapshot
such as:

`retro-boreal-2027.snapshot-2027-02-14-1530.xlsx`

Normal report generation must not mutate the workbook unless explicitly
documented.

------------------------------------------------------------------------

# 5. Core Workbook Sheets

Keep the manually maintained schema compact.

## 5.1 `Competitions`

One row per competition.

Minimum columns:

  -----------------------------------------------------------------------
  Column                  Required                Meaning
  ----------------------- ----------------------- -----------------------
  `competition`           yes                     Unique human-readable
                                                  competition name/key

  `scoring_method`        yes                     `callback` or `skating`

  `alternate_enabled`     callback only           TRUE/FALSE; whether
                                                  Alternate is available

  `status`                recommended             e.g. `setup`, `ready`,
                                                  `scored`, `published`

  `notes`                 no                      Organizer notes
  -----------------------------------------------------------------------

Possible future columns may include round, schedule time, division, or
display title, but do not add them until useful.

Validation:

-   competition names must be nonblank;
-   competition names must be unique;
-   `scoring_method` must be a supported value;
-   `alternate_enabled` is ignored for skating competitions.

## 5.2 `CompetitionJudges`

Association between competition and judge.

Minimum columns:

  Column          Required      Meaning
  --------------- ------------- ---------------------------------------
  `competition`   yes           Must match `Competitions.competition`
  `judge`         yes           Human-readable judge name
  `order`         recommended   Stable display/print order

No global judge registry is required.

The same judge string may appear in multiple competitions.

Validation:

-   referenced competition exists;
-   judge is nonblank;
-   same judge cannot appear twice in the same competition;
-   order values, if present, should be unique within a competition.

## 5.3 `CompetitionEntries`

Association between competition and competitor/couple/entry.

Minimum columns:

  Column          Required      Meaning
  --------------- ------------- --------------------------------------------
  `competition`   yes           Must match `Competitions.competition`
  `entry`         yes           Human-readable competitor/couple name
  `number`        recommended   Bib/call number shown on cards and reports
  `order`         recommended   Registration/call order

Examples of `entry`:

-   `Alice Tremblay`
-   `Alice Tremblay & Bob Smith`
-   `The Hot Shots`

For now, the application does not need to know whether the string
represents a solo competitor, couple, or team.

Validation:

-   referenced competition exists;
-   entry is nonblank;
-   duplicate entry strings within a competition are rejected or clearly
    warned;
-   duplicate numbers within a competition are rejected;
-   numbers are display identifiers, not database identities.

------------------------------------------------------------------------

# 6. Score-Entry Sheets

The CLI should generate score-entry worksheets from the three core setup
sheets.

These sheets are intentionally optimized for fast manual transcription
from paper scorecards.

Recommended naming should be deterministic and Excel-safe.

Example:

-   `Score - Open MixMatch`
-   `Score - Advanced Strictly`

If names would exceed Excel limits or collide, generate a stable
shortened form and clearly report the mapping.

## 6.1 Skating score-entry layout

Recommended matrix:

  Entry           Number   Judge A   Judge B   Judge C   Judge D   Judge E
  ------------- -------- --------- --------- --------- --------- ---------
  Alice & Bob        101
  Carol & Dan        102

Important:

-   workbook-facing judge columns may display actual judge names if
    useful to organizers;
-   the CLI must maintain a deterministic judge ordering;
-   every judge must provide exactly one valid ordinal rank for every
    entry;
-   normally each judge's column should contain a permutation of `1..N`;
-   blank/incomplete data must block final computation;
-   duplicate ranks, non-integers, and out-of-range ranks must block
    computation.

Do **not** silently convert missing ranks to `N+1` in this redesign. A
live competition result should not be produced from incomplete skating
marks without an explicit future rule allowing it.

## 6.2 Callback score-entry layout

Recommended matrix:

  Entry     Number Judge A   Judge B   Judge C   Judge D   Judge E
  ------- -------- --------- --------- --------- --------- ---------
  Alice        201
  Bob          202

Accepted values should be easy to type and normalized by the CLI.

Canonical values:

-   `Y` = Yes
-   `N` = No
-   `A` = Alternate, when enabled

Allow reasonable case-insensitive aliases such as `yes`, `no`, `alt`,
but write/report canonical values.

If `alternate_enabled = FALSE`, `A` must be rejected.

### Callback aggregation

The owner-approved schema-version-1 policy is:

-   Yes = 1;
-   Alternate = 0.5 when enabled;
-   No = 0;
-   order by total, then Yes count, then Alternate count;
-   advance the configured number of entries and include every entry tied
    at the boundary on all three ordering values.

Blank or unknown marks block final computation. The Alternate value is an
event policy, not a claimed universal Lindy Hop standard. Each callback
competition records `callback_advance_count` in its `Competitions` row.

For implementation, separate:

1.  mark normalization;
2.  aggregation;
3.  selection/cutoff policy.

Do not bury these rules in worksheet formulas.

The engine and every result report must expose these policy values rather
than relying on hidden worksheet formulas or defaults.

------------------------------------------------------------------------

# 7. Generated Pre-Competition Documents

The CLI must be able to generate printable PDFs before any marks are
entered.

## 7.1 Competitor call / registry sheets

Generate one page per competition.

Purpose:

-   MC call sheet;
-   registration/check-in helper;
-   staging helper;
-   quick reference for organizers.

Minimum content:

-   event name;
-   competition name;
-   scoring method;
-   entries in call/order sequence;
-   entry number;
-   entry string;
-   optional checkbox/blank area for manual notes.

Command concept:

`skating-system generate call-sheets event.xlsx`

Output example:

`reports/call-sheets.pdf`

Each competition begins on a new page.

## 7.2 Judge scorecards

Generate a scorecard for each judge × competition assignment.

Each scorecard should clearly contain:

-   event;
-   competition;
-   judge name;
-   scoring method;
-   complete ordered entry list;
-   bib/entry number;
-   space to mark rank or callback;
-   concise scoring instructions appropriate to the method.

For skating:

-   provide a rank column;
-   state that 1 is best;
-   state that every entry must receive exactly one rank;
-   no duplicate ranks.

For callback:

-   provide Yes / No;
-   provide Alternate only when enabled.

Command concept:

`skating-system generate judge-cards event.xlsx`

Output:

`reports/judge-cards.pdf`

Layout/aesthetics are secondary in v1. Prioritize legibility and
unambiguous data entry.

------------------------------------------------------------------------

# 8. CLI Workflow

The CLI should be command-oriented rather than interactive/TUI-first.

Suggested executable:

`skating-system`

or preserve the existing project executable if already packaged.

## 8.1 Inspect / validate

`skating-system validate event.xlsx`

Checks:

-   workbook schema;
-   required sheets;
-   competition references;
-   duplicates;
-   judge assignments;
-   entry assignments;
-   score-sheet presence/schema;
-   mark completeness;
-   mark validity;
-   readiness to compute.

Output should distinguish:

-   ERROR --- blocks computation;
-   WARNING --- suspicious but allowed;
-   INFO --- useful status.

Return nonzero exit status when errors exist.

## 8.2 Build/refresh generated score sheets

`skating-system build-sheets event.xlsx`

Responsibilities:

-   create missing score-entry sheets;
-   detect structural drift;
-   preserve already entered marks whenever safely possible;
-   never silently erase marks;
-   if a requested rebuild could lose data, stop and require an explicit
    destructive option or snapshot.

Potential explicit destructive form:

`skating-system build-sheets event.xlsx --rebuild`

Before destructive changes, create a workbook snapshot.

## 8.3 Generate operational documents

Examples:

`skating-system generate call-sheets event.xlsx`

`skating-system generate judge-cards event.xlsx`

A convenience command may generate both:

`skating-system generate pre-event event.xlsx`

## 8.4 Compute

`skating-system compute event.xlsx`

or:

`skating-system compute event.xlsx --competition "Open Mix & Match"`

Computation must always validate first.

Do not produce an apparently final result when blocking validation
errors exist.

## 8.5 Generate reports

Examples:

`skating-system report public event.xlsx`

`skating-system report management event.xlsx`

`skating-system report mc event.xlsx`

Convenience:

`skating-system report all event.xlsx`

Reports should be deterministic for identical workbook contents.

------------------------------------------------------------------------

# 9. Skating-System Engine

## 9.1 Existing engine is candidate code, not trusted truth

The repository already contains a substantial Rules 5--8 implementation,
derived tables, decision transcripts, and tests.

Preserve this code initially so useful work is not discarded.

However:

**Do not assume the current implementation is correct merely because its
existing tests pass.**

There is an unconfirmed concern that last year's competition may have
exposed scoring errors.

The redesign therefore includes a formal scoring-engine verification
milestone before live use.

## 9.2 Required verification work

Before integrating the engine into final reporting:

1.  Identify the exact published Skating System rulebook/reference the
    event intends to follow.
2.  Document that reference and version/date.
3.  Re-derive Rules 5--8 independently from the reference.
4.  Review the existing implementation line by line against that
    derivation.
5.  Reproduce all official worked examples available in the reference.
6.  Add adversarial test matrices, especially cases with strongly split
    judges.
7.  Add regression tests for any historical competition data that can be
    recovered.
8.  If last year's controversial result can be reconstructed, run it
    through:
    -   the existing engine;
    -   an independently implemented/reference calculation;
    -   manual calculation if practical.
9.  Document any discrepancy before modifying the engine.
10. Only after agreement, make the verified implementation
    authoritative.

## 9.3 Important adversarial cases

Tests must include:

-   unanimous rankings;
-   clear simple majority;
-   no majority at rank 1;
-   greater-majority resolution;
-   equal-majority/lower-sum resolution;
-   escalation across multiple rank thresholds;
-   extreme split opinions, including first-place vs last-place marks;
-   circular-looking preferences across judges;
-   exact ties;
-   maximum-depth tie resolution;
-   odd and even judge counts if allowed;
-   3, 5, 7+ judge panels;
-   different entry counts.

## 9.4 Explainability

The current concept of a deterministic decision transcript is valuable
and should remain.

For every skating computation, retain enough derived information to
answer:

-   at what threshold was the placement decided?
-   what majority/count was found?
-   when applicable, what rank sum broke the tie?
-   which rule resolved the placement?
-   if the threshold expanded, why?

The report layer must consume solver output. It must not independently
reconstruct or reinterpret the scoring logic.

------------------------------------------------------------------------

# 10. Reporting

Generate PDFs directly in v1.

A report run should create a timestamped or event-specific output
directory such as:

`reports/2027-02-14/`

or a simple deterministic `reports/` directory if preferred initially.

## 10.1 Public results report

Purpose:

-   transparency to competitors;
-   publication after results;
-   demonstrate how the panel voted without identifying individual
    judges.

For each competition include:

-   event;
-   competition;
-   scoring method;
-   final placement/selection;
-   entry number;
-   entry name/string;
-   anonymized judge columns.

Example skating table:

  Entry               A   B   C   D   E   Final
  ----------------- --- --- --- --- --- -------
  101 Alice & Bob     1   1   6   2   1       1
  102 Carol & Dan     2   2   1   1   2       2

Judge labels are assigned deterministically for that generated report:

`A`, `B`, `C`, ...

The public report MUST NOT include a mapping from those letters to
actual names.

For callback competitions, show anonymous judge marks and the final
callback/selection outcome.

The report should also state the scoring method used.

For skating competitions, include a concise explanation of the governing
Relative Placement / Skating rules or reference to the published event
rules.

## 10.2 Management / audit report

Purpose:

-   organizer verification;
-   dispute handling;
-   archival audit trail.

Include everything in the public report plus:

-   actual judge names;
-   mapping of judge letters to names;
-   raw marks;
-   validation status;
-   derived computation data needed to audit results;
-   full Skating System decision transcript;
-   generation timestamp;
-   application version / git commit when available;
-   workbook filename;
-   ideally a workbook content hash or equivalent audit identifier.

This report should make it possible to reconstruct why a placement
occurred.

## 10.3 MC results one-pager

Purpose:

-   announce results quickly;
-   no unnecessary scoring detail.

One competition per page.

Include:

-   event;
-   competition;
-   final placements or callback list;
-   entry number;
-   entry name/string.

For finals, emphasize podium/result order.

For callback rounds, clearly identify advancing entries.

Keep typography large and easy to scan under event conditions.

## 10.4 Call sheets

As specified earlier, one competition per page with all registered
entries.

These are operational documents and may be generated before results
exist.

------------------------------------------------------------------------

# 11. Judge Anonymity

Public judge anonymity must be implemented in the reporting layer.

Rules:

-   actual judge names remain in the workbook;
-   management reports use actual names;
-   public reports replace names with letters;
-   letter assignment follows the competition's stable judge order;
-   public artifacts must not accidentally contain judge names in PDF
    metadata, hidden tables, filenames, footnotes, or debug output.

Do not anonymize by destructively modifying source data.

------------------------------------------------------------------------

# 12. Validation and Competition-Day Safety

Validation is a major feature, not an afterthought.

## 12.1 Structural validation

Check:

-   expected sheets exist;
-   expected columns exist;
-   no duplicate competition names;
-   all association rows reference existing competitions;
-   no duplicate judge assignment within a competition;
-   no duplicate entry assignment within a competition;
-   no duplicate entry numbers within a competition.

## 12.2 Skating mark validation

Before computation:

-   every judge has a mark for every entry;
-   marks are integers;
-   marks are in `1..N`;
-   each judge uses every rank exactly once;
-   no duplicate rank within a judge column.

Any failure blocks result computation.

## 12.3 Callback validation

Before computation:

-   every mark is an accepted value;
-   Alternate is rejected when disabled;
-   blank handling is explicit;
-   aggregation/cutoff policy is known and reportable.

## 12.4 Human-friendly errors

Bad:

`invalid rank mark at C17`

Better:

`Open Mix & Match: Judge "Jane Smith" ranked both entry 104 and entry 108 as 3rd.`

When useful, include the Excel cell reference as secondary information.

------------------------------------------------------------------------

# 13. Snapshot / Backup Behavior

Because Excel is the source of truth, protect it.

Commands that only read data or generate PDFs should not modify the
workbook.

Commands that restructure generated sheets should:

1.  determine whether existing data could be affected;
2.  create a timestamped snapshot before destructive modification;
3.  print the snapshot path;
4.  fail safely if the backup cannot be created.

Do not create needless snapshots for read-only operations.

------------------------------------------------------------------------

# 14. Migration from Current Project

Do not perform a blind rewrite.

## Preserve

Likely valuable:

-   Python package/project setup;
-   scoring engine, subject to verification;
-   scoring-engine tests;
-   official/reference fixtures;
-   decision transcript concepts;
-   useful display-label/report formatting helpers that are not
    Textual-specific.

## Replace or retire from the critical path

-   Textual application;
-   Textual screens/modals/widgets;
-   JSON as primary event persistence;
-   UUID-heavy event setup workflow;
-   separate Participant/Entry management UX;
-   TUI-based score entry.

Migration status: the Textual and JSON implementations were retired after the
verified scoring engine, reference fixtures, and decision transcripts were
migrated to the workbook CLI architecture.

## New modules --- suggested

Keep naming simple; exact structure may be adjusted.

``` text
src/skating_system/
    cli.py
    workbook/
        reader.py
        writer.py
        schema.py
        validation.py
        score_sheets.py
    scoring/
        skating.py
        callback.py
        models.py
    reports/
        public.py
        management.py
        mc.py
        call_sheets.py
        judge_cards.py
        pdf.py
```

Avoid unnecessary class hierarchies.

Plain dataclasses and functions are preferred.

------------------------------------------------------------------------

# 15. Internal Data Model

The workbook is intentionally denormalized, but internal parsing may
produce simple dataclasses.

Example conceptual structures:

``` python
@dataclass
class Competition:
    name: str
    scoring_method: str
    alternate_enabled: bool

@dataclass
class JudgeAssignment:
    competition: str
    judge: str
    order: int

@dataclass
class EntryAssignment:
    competition: str
    entry: str
    number: str
    order: int
```

Scoring input should be transformed into explicit method-specific
matrices after validation.

Do not leak Excel row/cell handling into the scoring engine.

------------------------------------------------------------------------

# 16. Dependencies

Prefer minimal, mature libraries.

Expected candidates:

-   `openpyxl` --- workbook read/write;
-   existing Python standard library / current project stack;
-   `reportlab` --- direct PDF generation;
-   `pytest` --- tests.

Do not introduce pandas unless it materially simplifies something that
cannot be kept clear with `openpyxl`.

Do not use LibreOffice as an application runtime dependency.

------------------------------------------------------------------------

# 17. Testing Strategy

## 17.1 Workbook parser tests

Test:

-   valid minimal workbook;
-   missing sheets;
-   missing columns;
-   duplicate competition;
-   broken competition references;
-   duplicate judge;
-   duplicate entry;
-   duplicate entry number;
-   stable ordering.

## 17.2 Generated score-sheet tests

Test:

-   correct rows/columns;
-   correct competition/judge/entry ordering;
-   callback vs skating layouts;
-   Alternate column/validation behavior;
-   preservation of existing marks on safe refresh;
-   destructive rebuild snapshot behavior.

## 17.3 Scoring tests

Skating engine verification is a separate critical milestone described
above.

Callback tests must cover:

-   all Yes;
-   all No;
-   mixed votes;
-   Alternate enabled/disabled;
-   ties;
-   cutoff boundary;
-   configurable Alternate behavior.

## 17.4 Report tests

At minimum assert:

-   public report contains no actual judge names;
-   management report does contain judge names;
-   public and management reports show identical underlying
    marks/results;
-   MC report contains correct ordered results;
-   call sheets contain every registered entry exactly once;
-   one competition per intended page;
-   generated PDFs are nonempty and readable.

## 17.5 End-to-end fixture

Maintain at least one complete sample event workbook.

Automated test:

1.  load workbook;
2.  validate;
3.  generate judge cards;
4.  generate call sheets;
5.  compute completed competitions;
6.  generate all reports;
7.  compare key extracted outputs or snapshots.

------------------------------------------------------------------------

# 18. Recommended Implementation Milestones

## Milestone 1 --- Workbook contract

-   Define workbook schema.
-   Add example workbook fixture.
-   Implement reader.
-   Implement validation.
-   No scoring changes.

**Done when:** CLI can inspect an event workbook and clearly report
valid/invalid setup.

## Milestone 2 --- Pre-event generation

-   Generate score-entry sheets.
-   Generate call sheets.
-   Generate judge scorecards.
-   Implement safe rebuild/snapshot behavior.

**Done when:** an organizer can prepare all paper materials from only
the three setup sheets.

## Milestone 3 --- Scoring engine audit

-   Freeze existing behavior.
-   Identify authoritative rule reference.
-   Independently derive Rules 5--8.
-   Add official examples.
-   Add adversarial split-panel cases.
-   Reconstruct historical data if available.
-   Document discrepancies.
-   Correct engine only after evidence is established.

**Done when:** skating results are independently defensible and
regression-tested.

This milestone is a **live-event release blocker**.

## Milestone 4 --- Callback engine

-   Implement Yes/No/optional Alternate parsing.
-   Finalize explicit Alternate weighting and selection policy with
    owner.
-   Add tests.
-   Make policy visible in reports.

## Milestone 5 --- Reports

Generate:

-   public anonymous results;
-   management/audit results;
-   MC results;
-   competitor call sheets.

**Done when:** one command can produce the event-day report package from
a completed workbook.

## Milestone 6 --- Retire Textual critical path

-   Make CLI the documented primary interface.
-   Remove Textual dependency if no remaining value.
-   Remove obsolete JSON/UI code only after useful scoring/reference
    code is safely migrated.

Completed: the CLI is the primary interface; Textual and JSON implementation
code and dependencies have been removed from the supported application.

------------------------------------------------------------------------

# 19. Proposed Competition-Day Workflow

## Before the event

1.  Create/open event workbook.
2.  Fill `Competitions`.
3.  Fill `CompetitionJudges`.
4.  Fill `CompetitionEntries`.
5.  Run:

``` bash
skating-system validate event.xlsx
skating-system build-sheets event.xlsx
skating-system generate pre-event event.xlsx
```

6.  Print:
    -   judge cards;
    -   call/registry sheets.

## During each competition

1.  Judges complete paper cards.
2.  Organizer collects cards.
3.  Staff manually enter marks into the corresponding Excel score sheet.
4.  Run:

``` bash
skating-system validate event.xlsx
```

5.  Resolve every error against the original paper cards.
6.  Compute:

``` bash
skating-system compute event.xlsx --competition "Competition Name"
```

7.  Generate immediate documents:

``` bash
skating-system report mc event.xlsx --competition "Competition Name"
skating-system report management event.xlsx --competition "Competition Name"
```

8.  Announce results.

## Publication

After verification:

``` bash
skating-system report public event.xlsx
```

Publish the resulting anonymous report.

------------------------------------------------------------------------

# 20. Product Decisions

### O-1 --- Callback Alternate weighting (resolved)

Yes = 1, No = 0, and optional Alternate = 0.5. Reports identify this as an
event policy rather than a universal Lindy Hop standard.

### O-2 --- Callback advancement cutoff (resolved)

Each callback competition stores a positive `callback_advance_count`. Entries
are ordered by total, Yes count, then Alternate count. Every entry tied at the
boundary on those values advances.

### O-3 --- Public skating explanation depth

Initial public report should expose anonymous raw ranks and final
result.

Management report gets the full transcript.

After seeing real PDFs, decide whether the public report should also
include a condensed rule-resolution explanation for surprising
placements.

------------------------------------------------------------------------

# 21. Explicit Non-Goals for This Version

Do not implement unless required by a discovered workflow problem:

-   relational person registry;
-   normalized couples;
-   UUID-facing workbook schema;
-   database server;
-   web application;
-   cloud synchronization;
-   live network judge entry;
-   judge authentication;
-   mobile scoring;
-   elaborate PDF styling;
-   multi-user workbook locking;
-   advanced historical analytics;
-   automatic competitor deduplication;
-   multi-dance Rules 9--11 unless explicitly requested later.

------------------------------------------------------------------------

# 22. Definition of Done

The redesign is complete when:

1.  One Excel workbook can define an entire event.
2.  The three core setup tables are sufficient to generate competition
    materials.
3.  Judges and entries are human-readable strings.
4.  The CLI validates the workbook with actionable errors.
5.  The CLI generates score-entry sheets safely.
6.  The CLI generates judge scorecards as PDF.
7.  The CLI generates one-competition-per-page call sheets as PDF.
8.  Callback competitions support Yes/No and optional Alternate.
9.  Skating competitions use a reviewed and independently verified Rules
    5--8 implementation.
10. Incomplete/invalid skating marks cannot silently produce final
    results.
11. Public PDFs show anonymous judge columns.
12. Management PDFs show actual judge identities and full audit
    information.
13. MC PDFs provide simple announcement-ready results.
14. Read-only reporting never modifies the workbook.
15. Potentially destructive workbook operations create snapshots.
16. The Textual TUI is no longer required for the competition-day
    workflow.
17. Automated tests cover workbook validation, scoring, anonymity,
    reports, and at least one end-to-end event fixture.

------------------------------------------------------------------------

# 23. Agent Guidance

Treat this handoff as a product-direction reset.

Do not attempt to preserve the existing Textual workflow merely because
code already exists.

Conversely, do not throw away the scoring engine and its fixtures merely
because the UI is being replaced.

The highest-risk component is **scoring correctness**, especially
unusual panels where judges disagree strongly. Make that logic boring,
explicit, tested, and independently reproducible.

The highest-value UX characteristic is **operational simplicity**:

> edit Excel → validate → compute → generate PDFs

If an implementation choice makes that workflow harder to understand or
recover manually during a live competition, prefer the simpler choice.
