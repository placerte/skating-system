# AGENTS.md

### LLM Context Blocks

These files contain reusable instructions and workflows
that may be relevant when working in this repository.

<!-- agmod:start -->

- llm/agent_executor_instructions_v_1.md
- llm/app_dev_execution_starter_v1.md
- llm/code_style.md
- llm/decision_log.md
- llm/general_executor_instructions_v1.md
- llm/git_hosting_toolbox.md
- llm/pdf_toolbox.md
- llm/project_handoff_standard_v1.md
- llm/project_operating_model_v1.md
- llm/python_toolbox.md
- llm/sessions_logger.md
- llm/user-persona.md

<!-- agmod:end -->


This file orients agentic coders working in this repository.
Follow project conventions and keep changes aligned with the domain specs.

## Project snapshot

- Language: Python 3.13 (see `pyproject.toml`).
- Package root: `src/skating_system`.
- Interface: command-oriented CLI (workbook workflow under development).
- Persistence: Excel workbook; legacy JSON remains temporarily during migration.
- Formatting: Black.
- Type checking: Pyright config present (`pyrightconfig.json`).

Owner preferences:

- Author is a mechanical engineer and coding hobbyist.
- Prefer simple, readable code over heavy architecture patterns.
- Smaller files with small, focused functions are preferred.

Additional preferences from `persona.md`:

- Technical, pragmatic; optimize for clarity and control over elegance.
- Prefer explicit logic (simple loops/ifs) over dense comprehensions or abstractions.
- Avoid "magic" and reflection (e.g., `getattr`, dynamic wiring) unless clearly justified.
- Keep tooling minimal and Linux/CLI-friendly; `uv` is the default.
- When making tradeoffs, state assumptions and keep changes small; expand only when needed.

Authoritative docs:

- Domain rules: `docs/specs.md`.
- Clarifications: `docs/specs_details.md`.
- Spec tracking: `docs/spec_tracking.md`.
- UI intent and flow: `docs/ui_intent.md`.
- Module boundaries: `docs/implementation.md`.

## Repository layout

Current package layout:

- `src/skating_system/domain`: dataclasses + validation.
- `src/skating_system/persistence`: legacy JSON file I/O and migrations.
- `src/skating_system/services`: legacy orchestration retained during migration.
- `src/skating_system/workbook`: workbook schema, parsing, and safe updates.
- `src/skating_system/scoring`: method-specific scoring engines.
- `src/skating_system/reports`: generated PDF documents.

Keep these boundaries strict. Avoid I/O imports in domain/scoring.

## Build, lint, and test commands

The repo uses uv for builds/installs (see `uv.lock`).
Prefer uv, but include pip/venv fallback where needed.

### Setup

- Create venv (uv): `uv venv --python 3.13`
- Install deps (uv): `uv sync`
- Fallback (pip): `python -m venv .venv && .venv/bin/pip install -e .`

### Inspect the CLI

- CLI help (uv): `uv run python -m skating_system --help`
- Fallback: `.venv/bin/python -m skating_system`

### Formatting (Black)

- Check format: `uv run python -m black --check .`
- Format: `uv run python -m black .`

### Linting / type checks

No explicit linter config is present yet.
Type checking can be done with Pyright if installed:

- Type check (pyright): `uv run pyright`
- Fallback: `.venv/bin/pyright`

### Tests

Pytest is available and should be used for tests.

- Run all tests: `uv run python -m pytest`
- Single test file: `uv run python -m pytest tests/test_event_service.py`
- Single test case: `uv run python -m pytest tests/test_event_service.py -k test_name`

If pytest is not installed, add it as a dev dependency first.

## Code style and conventions

### Formatting

- Use Black defaults (88-char line length).
- Keep one logical statement per line.
- Use trailing commas in multi-line literals.

### Imports

- Order: standard library, third-party, local.
- Use absolute imports from `skating_system`.
- Avoid relative imports unless tightly scoped inside a package.
- Group imports with a single blank line between sections.

Example:

```python
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from skating_system.domain.models import Event
```

### Typing

- Use type hints on public functions and dataclasses.
- Prefer modern syntax: `list[str]`, `dict[str, int]`, `str | None`.
- Use `UUID` for domain identities; avoid plain `str` IDs.
- Keep `pyrightconfig.json` in mind; missing stubs are ignored.

### Naming

- Modules: snake_case.
- Classes: PascalCase.
- Functions/vars: snake_case.
- Constants: UPPER_SNAKE_CASE.
- Use domain terms consistently: Event, Participant, Entry, Competition, RankMark.

### Domain rules and data handling

- UUIDs are true identities; numbers/names are not.
- Use `is_obsolete` instead of deleting domain entities.
- Use the term "rank" everywhere; avoid "score".
- Allow ties in rankings; do not assume strict ordering.

### Error handling and validation

- Validation should return structured errors (e.g., list[str]) rather than raising.
- UI should show validation errors in context, not crash.
- Persistence should be resilient to missing/unknown fields.
- Never crash on user input; degrade gracefully.

### Boundaries and dependencies

- `domain/*`: pure data + validation only (no UI or I/O).
- `persistence/*`: file I/O + migrations only.
- `services/*`: orchestration used by the CLI.
- `workbook/*`: workbook schema, models, parsing, validation, and safe updates.
- `scoring/*`: method-specific scoring models and engines.
- `reports/*`: generated PDF documents.

### Comments and documentation

- Keep comments rare; prefer readable code.
- When non-obvious, add short rationale comments.
- Update docs in `docs/` when you change the domain model or flows.

## Operational guidance for agents

- Keep edits localized to relevant modules.
- Preserve existing file structure and naming.
- Avoid introducing new dependencies without updating `pyproject.toml`.
- Prefer small, testable changes over wide refactors.
- If you add tests, place them under `tests/` and follow pytest naming.

## Cursor / Copilot rules

- None found in `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md`.
