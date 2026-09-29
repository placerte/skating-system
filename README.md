# Skating System

Command-line tools for validating skating competition workbooks, computing
placements, and generating printable PDFs.

## Installation

Download the latest Linux binary and install it in `/usr/local/bin`:

```bash
curl -L -o skating-system \
  https://github.com/placerte/skating-system/releases/latest/download/skating-system-linux-x86_64

chmod +x skating-system
sudo mv skating-system /usr/local/bin/skating-system
```

## Current development usage

Show the workbook-oriented command surface:

```bash
skating-system --help
```

The workbook redesign is in progress. Commands that are not implemented yet
exit nonzero and identify their tracking issue. The intended workflow is:

```bash
skating-system validate event.xlsx
skating-system build-sheets event.xlsx
skating-system compute event.xlsx
skating-system report all event.xlsx
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
```
