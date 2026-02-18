# Release v0.2.0

## GitHub Release Fields

- Title: v0.2.0
- Tag: v0.2.0
- Target: main
- Release type: stable

## Summary

UI/UX polish for the Textual app, including better navigation, safer competition actions, clipboard/export utilities, and clearer validation messaging. No scoring or transcript logic changes.

## What's Changed

- Home table navigation gains vim keys, Enter opens edit, and copy/export actions.
- Duplicate and delete competition workflows added (soft-delete with confirmation).
- Competition screen now defaults to a collapsed transcript panel.
- CSV export for visible tables and TSV yank to clipboard.
- Validation messaging uses judge/entry names instead of UUIDs.
- Dead-cell cutoff visualization aligns with transcript decisions in block resolutions.
- Figlet title centering adjusted for consistent alignment.

## Assets

- Source archives (GitHub auto-generated)
- Optional: PyInstaller binary build (if produced)

## Checks

- `uv run python -m pytest`

## Notes

- No data migrations required.
- If distributing a binary, ensure `skating-system.spec` is used for PyInstaller.
