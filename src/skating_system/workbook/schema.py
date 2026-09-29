from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

# GitHub issue #2: define the versioned workbook contract.
SCHEMA_VERSION: Final = "1"

EVENT_SHEET: Final = "Event"
COMPETITIONS_SHEET: Final = "Competitions"
JUDGES_SHEET: Final = "CompetitionJudges"
ENTRIES_SHEET: Final = "CompetitionEntries"

SCORING_METHOD_CALLBACK: Final = "callback"
SCORING_METHOD_SKATING: Final = "skating"
SCORING_METHODS: Final = frozenset({SCORING_METHOD_CALLBACK, SCORING_METHOD_SKATING})

SCORE_SHEET_PREFIX: Final = "Score - "
EXCEL_SHEET_NAME_LIMIT: Final = 31

_INVALID_SHEET_CHARACTERS = re.compile(r"[\[\]:*?/\\]")
_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class SheetContract:
    """Required and optional columns for one manually maintained sheet."""

    name: str
    required_columns: tuple[str, ...]
    optional_columns: tuple[str, ...] = ()

    @property
    def columns(self) -> tuple[str, ...]:
        return self.required_columns + self.optional_columns


EVENT_CONTRACT: Final = SheetContract(
    name=EVENT_SHEET,
    required_columns=("field", "value"),
)
COMPETITIONS_CONTRACT: Final = SheetContract(
    name=COMPETITIONS_SHEET,
    required_columns=("competition", "scoring_method"),
    optional_columns=("alternate_enabled", "status", "notes"),
)
JUDGES_CONTRACT: Final = SheetContract(
    name=JUDGES_SHEET,
    required_columns=("competition", "judge"),
    optional_columns=("order",),
)
ENTRIES_CONTRACT: Final = SheetContract(
    name=ENTRIES_SHEET,
    required_columns=("competition", "entry"),
    optional_columns=("number", "order"),
)
CORE_SHEETS: Final = (
    EVENT_CONTRACT,
    COMPETITIONS_CONTRACT,
    JUDGES_CONTRACT,
    ENTRIES_CONTRACT,
)


def normalize_header(value: object) -> str:
    """Return the canonical comparison form for a workbook column heading."""

    return normalize_text(value).casefold().replace(" ", "_")


def normalize_text(value: object) -> str:
    """Trim a workbook value and collapse runs of whitespace."""

    if value is None:
        return ""
    return _WHITESPACE.sub(" ", str(value).strip())


def comparison_key(value: object) -> str:
    """Return a case-insensitive key without changing displayed text."""

    return normalize_text(value).casefold()


def score_sheet_names(competition_names: list[str]) -> dict[str, str]:
    """Build deterministic, Excel-safe score-sheet names in input order.

    Excel treats sheet names case-insensitively. Collisions therefore receive a
    numeric suffix while preserving the 31-character limit.
    """

    result: dict[str, str] = {}
    used_names: set[str] = set()

    for competition_name in competition_names:
        display_name = normalize_text(competition_name)
        safe_name = _INVALID_SHEET_CHARACTERS.sub("-", display_name)
        safe_name = normalize_text(safe_name).strip("'") or "Competition"
        base_name = f"{SCORE_SHEET_PREFIX}{safe_name}"
        candidate = base_name[:EXCEL_SHEET_NAME_LIMIT].rstrip()
        suffix_number = 2

        while candidate.casefold() in used_names:
            suffix = f" ~{suffix_number}"
            available = EXCEL_SHEET_NAME_LIMIT - len(suffix)
            candidate = f"{base_name[:available].rstrip()}{suffix}"
            suffix_number += 1

        result[competition_name] = candidate
        used_names.add(candidate.casefold())

    return result
