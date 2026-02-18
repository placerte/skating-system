from __future__ import annotations

import csv
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.text import Text
from textual.widgets import DataTable


def datatable_to_rows(table: DataTable) -> tuple[list[str], list[list[str]]]:
    headers: list[str] = []
    columns: Any = table.columns
    if isinstance(columns, Mapping):
        for column in columns.values():
            headers.append(_stringify(getattr(column, "label", column)))
    else:
        for column_key in columns:
            column: Any = None
            if hasattr(table, "get_column"):
                try:
                    column = table.get_column(column_key)
                except (KeyError, AttributeError):
                    column = None
            label = (
                column_key if column is None else getattr(column, "label", column_key)
            )
            headers.append(_stringify(label))
    rows: list[list[str]] = []
    for row_index in range(table.row_count):
        row_values = table.get_row_at(row_index)
        rows.append([_stringify(cell) for cell in row_values])
    return headers, rows


def datatable_to_tsv_text(table: DataTable) -> str:
    headers, rows = datatable_to_rows(table)
    lines: list[str] = []
    if headers:
        lines.append("\t".join(headers))
    for row in rows:
        lines.append("\t".join(row))
    return "\n".join(lines)


def export_datatable_to_csv(table: DataTable, output_path: Path) -> None:
    headers, rows = datatable_to_rows(table)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)


def default_export_dir() -> Path:
    return Path.cwd() / "exports"


def build_export_path(
    base_dir: Path,
    *,
    event_name: str | None,
    competition_name: str | None,
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parts = [_slugify(part) for part in (event_name, competition_name) if part]
    base = "_".join(part for part in parts if part) or "export"
    filename = f"{base}_{timestamp}.csv"
    return base_dir / filename


def _stringify(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, Text):
        return value.plain
    return str(value)


def _slugify(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return ""
    chars: list[str] = []
    for char in cleaned:
        if char.isascii() and char.isalnum():
            chars.append(char)
        elif char in {"-", "_"}:
            chars.append(char)
        elif char == " ":
            chars.append("_")
        else:
            chars.append("_")
    slug = "".join(chars)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_-")
