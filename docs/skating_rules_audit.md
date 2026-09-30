# Rules 5–8 authority and implementation audit

Date: 2026-09-30
Issue: GitHub #8
Detailed research: `skating-system-references-deep-research-report.md`

## Adopted authority

Retro Boréal adopts Rules 5–8 of the WDSF-linked *The Skating System* as the
authority for single-competition relative placement. The reference is pinned
to the content audited on 2026-09-30 rather than to an indefinitely moving
“current WDSF rules” reference.

The dated corroborating edition is:

- Svenska Danssportförbundet, *The Skating System — Bedömningssystemet för
  Standard, Latin och 10-dans*, Version 1, 2024-09-01.

The organizer confirmed that judging panels always contain an odd number of
judges. Rules 9–11 and multi-dance aggregation are outside this implementation.

## Source provenance

| Artifact | Retrieval | Size | SHA-256 | Status |
|---|---:|---:|---|---|
| WDSF-linked 22-page teaching document, retrieved through the accessible MDSF mirror named in the research report | 2026-09-30 | 278,768 bytes | `8277051135f1732b0427c4a2ab285e6fa2b590bb0ad4a57fd7c7289420f73649` | Audited Rules 5–8 content; mirror bytes, not proof of byte identity with the interactive WDSF Box object |
| Svenska Danssportförbundet Version 1, 2024-09-01 | 2026-09-30 | 504,786 bytes | `d308d4da72d2f7634b6f673dafd4130cd6567bdc847b65e913582a306d4a5b90` | Dated federation corroboration; 19 pages |

Canonical links at audit time:

- WDSF document entry:
  `https://www.worlddancesport.org/Document/99473179446/The-Skating-System.pdf`
- WDSF Box target:
  `https://dancesport.app.box.com/s/w60qa4644xcfuggvq03ygjo3ksivwo1w`
- Audited accessible mirror:
  `https://madsf.mk/download_wdsf.php?file=6+-+The+Skating+System.pdf`
- Dated Swedish edition:
  `https://www.danssport.se/media/z3jlnzuj/the-skating-system-slt-2024-09-01.pdf`

The PDFs are not committed. Their identity and retrieval context are recorded
so a reviewer can reproduce the comparison without treating mutable URLs as
versions. The official WDSF endpoint returned an interactive HTML/Box response
to non-browser retrieval, so this audit does not claim that the mirror and Box
objects are byte-identical.

## Independent derivation

For `N` entries and odd `J` judges, each judge must submit the complete strict
permutation `1..N`. The majority is:

```text
M = (J + 1) / 2
```

At cumulative threshold `t`:

```text
C(entry, t) = count of ranks <= t
S(entry, t) = sum of ranks <= t
```

The next place is determined as follows:

1. If nobody has `C >= M`, increase `t` for the full unplaced field (Rule 8).
2. If one entry has a majority, it takes the next place (Rule 5).
3. If several have a majority, the larger `C` wins (Rule 6).
4. Equal counts are resolved by the smaller `S` (Rule 7).
5. A subgroup still tied on count and sum advances alone to `t + 1`.
6. A tie still exact at `t = N` shares the arithmetic mean of its consecutive
   occupied places. All occupied slots are consumed.

Missing entries or ranks, duplicate ranks, judge-created ties, non-integer
ranks, and out-of-range ranks are invalid ballots. They block calculation and
must not be repaired by the scoring algorithm. Silently removing a judge would
change both the panel and its majority and is not permitted.

## Evidence and observed behavior

`tests/test_skating_rules_audit.py` independently transcribes the official Rule
5, 6, 7, and 8 matrices. For every entry it asserts:

- the published final ordering;
- independently calculated cumulative count vectors;
- independently calculated cumulative sum vectors; and
- the required majority threshold.

All four examples passed against the pre-correction engine. This freezes the
candidate engine’s conforming behavior and found no Rules 5–8 calculation
discrepancy.

The owner’s odd-panel policy did expose one discrepancy: the pre-correction
engine accepted a complete two-judge panel and produced a shared result. The
new regression failed before the correction and now passes after
`validate_competition_ranks` was changed to reject non-empty even panels. The
legacy terminal-tie fixture was changed from four judges to a valid three-judge
permutation while preserving its 1.5 shared-place expectation.

## Known defects in the teaching text

Two internally contradicted phrases are treated as publication errors, not
alternate rules:

- The Rule 6 narrative says “4th place and higher” after advancing to the
  `1–5` column. Its matrix gives competitor 65 three ranks at `1–4` and five at
  `1–5`; the table and outcome require “5th place and higher.”
- The Rule 7 continuation names competitor 85 in a field numbered 71–76. The
  matrix and surrounding text identify competitor 75.

Neither typo is encoded in the implementation.

## Historical Short Showcase reconstruction

The companion `retro-boreal` repository preserves seven Short Showcase judge
sheets across two photographs. That matches the seven judges recorded for
`Mini Showcases` in `rb26.json`; the JSON itself contains no saved rank marks.

Temporary rotated, per-sheet inspection produced a first transcription of each
handwritten `Position` column. The event owner then independently entered the
seven cards into `Retro-Boreal-2026-Ledger.xlsx`. The two transcriptions match,
including the overwritten and faint cells. The resulting entry-by-judge matrix
is frozen in `tests/test_skating_rules_audit.py`.

The reconstructed placement is:

| Place | Entry |
|---:|---|
| 1 | Yanik & Sydjie |
| 2 | Philippe & Caroline |
| 3 | Sébastien & Miriook |
| 4 | Florence & Anthony |
| 5 | Nathaniel & Geneviève |
| 6 | Jimmy & Myriam |
| 7 | Annie & Ludovic |
| 8.5 | Karell & Guillaume |
| 8.5 | Sydjie & Philippe |

The final two entries remain exactly tied through cumulative column `1–9` on
both count and sum. They therefore share the mean of eighth and ninth place,
`8.5`, under Rule 7. The legacy JSON contains no stored Showcase marks or
computed result, so there is no preserved legacy software output against which
to claim a calculation discrepancy.

## Audit conclusion

The existing engine reproduces all four adopted federation Rules 5–8 examples,
including Rule 8’s late-majority behavior. Its count-before-sum precedence,
tied-subgroup recursion, terminal shared-place mean, and placement consumption
agree with the independently derived procedure.

The one confirmed local-policy defect—acceptance of even judging panels—has a
documented failing regression and is corrected. The independently verified
historical Short Showcase matrix produces a terminal 8.5/8.5 shared placement.
The evidence required by issue #8 is complete.
