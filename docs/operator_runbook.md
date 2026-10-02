# Competition-day operator runbook

The Excel workbook is the event record. Generated worksheets and PDFs can be
recreated; do not maintain a parallel JSON event file.

## Prepare the event

1. Copy a known-good workbook or create the four core sheets described in
   `docs/workbook_contract_v1.md`.
2. Enter competitions, assigned judges, entries, entry numbers, and stable
   display order.
3. For callback competitions, set `alternate_enabled` and a positive
   `callback_advance_count`.
4. Create the score-entry sheets:

   ```bash
   skating-system build-sheets event.xlsx
   ```

5. Generate and print the operational documents:

   ```bash
   skating-system generate pre-event event.xlsx
   ```

This creates call sheets and one scorecard for every assigned judge. Keep the
paper cards as the authoritative transcription source.

## Enter and verify marks

Enter ranks or callbacks in the generated `Score - ...` worksheets. Do not
reorder or rename generated columns while marks are present.

Run validation after each transcription batch:

```bash
skating-system validate event.xlsx
```

Resolve every `ERROR` against the paper card. Blank, duplicate, out-of-range,
or incomplete skating ranks block computation. Unknown callback values and an
Alternate mark when Alternate is disabled also block computation.

## Compute during the event

Compute one ready competition while later competitions remain incomplete:

```bash
skating-system compute event.xlsx --competition "Open Mix & Match"
```

When the whole workbook is complete:

```bash
skating-system compute event.xlsx
```

Computation is read-only. Results are derived from workbook marks and are not
stored as hidden authoritative state.

## Generate result documents

For one competition:

```bash
skating-system report public event.xlsx --competition "Open Mix & Match"
skating-system report management event.xlsx --competition "Open Mix & Match"
skating-system report mc event.xlsx --competition "Open Mix & Match"
```

For every completed competition:

```bash
skating-system report all event.xlsx
```

- `public-results.pdf` contains anonymous judge columns, raw marks, and final
  outcomes. The owner selected concise public output; detailed Skating System
  resolution is intentionally omitted.
- `management-results.pdf` contains judge identities, source marks, derived
  tables, full decision transcripts, policy, workbook hash, and build
  provenance.
- `mc-results.pdf` contains only announcement-ready placements or advancing
  callback entries, one competition per page.

Review the management report against the paper cards before publication. Use
the MC report for announcements, then publish the public report.

## Recovery and safe rebuilding

Normal validation, computation, and report generation do not modify the
workbook. `build-sheets` preserves mapped marks and refuses ambiguous changes.

If assignments changed and a score sheet cannot be refreshed safely:

1. Close the workbook in Excel or LibreOffice.
2. Preserve the paper cards and inspect the reported unmapped cells.
3. Run the explicit rebuild:

   ```bash
   skating-system build-sheets event.xlsx --rebuild
   ```

4. Confirm the command reports a timestamped snapshot path before relying on
   the rebuilt workbook.
5. Re-enter or verify marks against the original cards, then validate again.

Never delete the snapshot until the event and published results have been
audited. If a generated PDF is wrong, correct the workbook, validate, compute,
and regenerate it; do not edit the PDF as a substitute for correcting source
data.
