# Skating System

Terminal UI for managing skating competitions and computing placements using the official skating system rules.

## Installation

Download the latest Linux binary and install it in `/usr/local/bin`:

```bash
curl -L -o skating-system \
  https://github.com/placerte/skating-system/releases/latest/download/skating-system-linux-x86_64

chmod +x skating-system
sudo mv skating-system /usr/local/bin/skating-system
```

## Usage

Launch the app:

```bash
skating-system
```

Open a specific event file:

```bash
skating-system ./path/to/event.json
```

Start from a directory (auto-picks `event.json` or the only `.json` file):

```bash
skating-system .
```

## Development

Create a virtual environment and install deps:

```bash
uv venv --python 3.13
uv sync
```

Run the app:

```bash
uv run python -m skating_system
```

Run tests:

```bash
uv run python -m pytest
```
