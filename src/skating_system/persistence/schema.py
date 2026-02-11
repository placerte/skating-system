from __future__ import annotations

from typing import Any

CURRENT_SCHEMA_VERSION = 1


def read_schema_version(raw: dict[str, Any]) -> tuple[int | None, list[str]]:
    warnings: list[str] = []
    schema_version = raw.get("schema_version")
    app_version = raw.get("app_version")

    if schema_version is None and app_version is None:
        warnings.append("Missing schema_version or app_version.")

    if schema_version is not None and schema_version != CURRENT_SCHEMA_VERSION:
        warnings.append(
            "Schema version mismatch: expected "
            f"{CURRENT_SCHEMA_VERSION}, got {schema_version}."
        )

    if schema_version is None and app_version is not None:
        warnings.append("Using app_version without schema_version.")

    return schema_version, warnings
