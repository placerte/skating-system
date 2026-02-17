from __future__ import annotations

import argparse
from pathlib import Path

from skating_system.ui.app import run


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="skating-system",
        description="Skating system Textual UI",
    )
    parser.add_argument(
        "event_path",
        nargs="?",
        help="Path to event JSON file (default: search current directory)",
    )
    args = parser.parse_args(argv)

    event_path, warning = _resolve_event_path(args.event_path)
    initial_warnings = [warning] if warning else None
    run(initial_path=event_path, initial_warnings=initial_warnings)


def _resolve_event_path(raw: str | None) -> tuple[Path | None, str | None]:
    if raw is None or raw == ".":
        return _find_event_in_dir(Path.cwd())

    path = Path(raw)
    if path.is_dir():
        return _find_event_in_dir(path)
    if path.suffix == "" and not path.exists():
        path = path.with_suffix(".json")
    return path, None


def _find_event_in_dir(directory: Path) -> tuple[Path | None, str | None]:
    if not directory.exists():
        return None, f"Directory not found: {directory}"
    if not directory.is_dir():
        return None, f"Not a directory: {directory}"

    preferred = directory / "event.json"
    if preferred.exists():
        return preferred, None

    candidates = sorted(directory.glob("*.json"))
    if len(candidates) == 1:
        return candidates[0], None
    if len(candidates) > 1:
        return None, f"Multiple .json files in {directory}. Specify one."
    return None, f"No .json event found in {directory}."


if __name__ == "__main__":
    main()
