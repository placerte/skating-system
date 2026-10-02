# Skating System

Command-line tools for running an Excel-workbook-based dance competition:
validate setup and marks, print operational documents, compute callback or
Skating System results, and generate public, management, and MC PDFs.

## Installation

Download the latest Linux binary and install it in `/usr/local/bin`:

```bash
curl -L -o skating-system \
  https://github.com/placerte/skating-system/releases/latest/download/skating-system-linux-x86_64

chmod +x skating-system
sudo mv skating-system /usr/local/bin/skating-system
```

## Competition-day workflow

The `.xlsx` workbook is the single editable source of truth. JSON files and the
retired Textual interface are not part of the competition-day workflow.

Prepare the score-entry sheets and printable documents:

```bash
skating-system build-sheets event.xlsx
skating-system generate pre-event event.xlsx
```

Enter marks directly into the generated `Score - ...` sheets, then validate
before computing anything final:

```bash
skating-system validate event.xlsx
skating-system compute event.xlsx
skating-system report all event.xlsx
```

Use `--competition "Competition Name"` with `compute` or any `report` command
to process one ready competition while others are still incomplete.

See [docs/operator_runbook.md](docs/operator_runbook.md) for workbook setup,
live-event operation, recovery, and publication procedures. The workbook
contract is documented in
[docs/workbook_contract_v1.md](docs/workbook_contract_v1.md).

## Commands

```text
validate WORKBOOK
build-sheets WORKBOOK [--rebuild]
generate call-sheets WORKBOOK
generate judge-cards WORKBOOK
generate pre-event WORKBOOK
compute WORKBOOK [--competition NAME]
report public WORKBOOK [--competition NAME]
report management WORKBOOK [--competition NAME]
report mc WORKBOOK [--competition NAME]
report all WORKBOOK [--competition NAME]
```

## Development

Create a virtual environment and install deps:

```bash
uv venv --python 3.13
uv sync
```

Inspect the CLI:

```bash
uv run python -m skating_system --help
```

Run tests:

```bash
uv run python -m pytest
uv run python -m black --check .
uv run pyright
```
