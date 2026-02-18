from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from skating_system.domain.models import (
    Competition,
    Entry,
    EntryMember,
    Event,
    Participant,
    RankMark,
)
from skating_system.persistence.schema import read_schema_version


class JsonEventRepo:
    def __init__(self) -> None:
        self._unknown_top_level: dict[str, Any] = {}

    def load_event(self, file_path: Path) -> tuple[Event, list[str]]:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
        warnings: list[str] = []

        schema_version, schema_warnings = read_schema_version(raw)
        warnings.extend(schema_warnings)

        known_keys = {
            "id",
            "name",
            "participants",
            "entries",
            "competitions",
            "created_at",
            "updated_at",
            "schema_version",
            "app_version",
        }
        self._unknown_top_level = {
            key: value for key, value in raw.items() if key not in known_keys
        }
        if self._unknown_top_level:
            warnings.append("Unknown top-level fields preserved.")

        event_id = _parse_uuid(raw.get("id"), warnings, "event.id")
        if event_id is None:
            event_id = uuid4()
            warnings.append("Generated new event id.")
        name = raw.get("name", "")

        participants = _load_participants(raw.get("participants", []), warnings)
        entries = _load_entries(raw.get("entries", []), warnings)
        competitions = _load_competitions(raw.get("competitions", []), warnings)

        event = Event(
            id=event_id,
            name=name,
            participants=participants,
            entries=entries,
            competitions=competitions,
            created_at=_parse_datetime(raw.get("created_at"), warnings, "event"),
            updated_at=_parse_datetime(raw.get("updated_at"), warnings, "event"),
            schema_version=schema_version,
            app_version=raw.get("app_version"),
        )
        return event, warnings

    def save_event(self, file_path: Path, event: Event) -> list[str]:
        warnings: list[str] = []
        payload = _dump_event(event)
        if self._unknown_top_level:
            payload = {**self._unknown_top_level, **payload}
            warnings.append("Unknown top-level fields preserved on save.")

        # Atomic-ish write: write to a temp file then replace.
        tmp_path = file_path.with_name(f"{file_path.name}.tmp")
        tmp_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        tmp_path.replace(file_path)
        return warnings


def _load_participants(
    raw_list: list[dict[str, Any]], warnings: list[str]
) -> list[Participant]:
    participants: list[Participant] = []
    for raw in raw_list:
        participant_id = _parse_uuid(raw.get("id"), warnings, "participant.id")
        if participant_id is None:
            continue
        participants.append(
            Participant(
                id=participant_id,
                number=int(raw.get("number", 0)),
                first_name=str(raw.get("first_name", "")),
                last_name=str(raw.get("last_name", "")),
                email=raw.get("email"),
                is_obsolete=bool(raw.get("is_obsolete", False)),
            )
        )
    return participants


def _load_entries(raw_list: list[dict[str, Any]], warnings: list[str]) -> list[Entry]:
    entries: list[Entry] = []
    for raw in raw_list:
        entry_id = _parse_uuid(raw.get("id"), warnings, "entry.id")
        if entry_id is None:
            continue
        members = [
            EntryMember(
                participant_id=member_id,
                role=member.get("role"),
            )
            for member in raw.get("members", [])
            if (
                member_id := _parse_uuid(
                    member.get("participant_id"), warnings, "entry.member"
                )
            )
            is not None
        ]
        entries.append(
            Entry(
                id=entry_id,
                name=str(raw.get("name", "")),
                members=members,
                is_obsolete=bool(raw.get("is_obsolete", False)),
            )
        )
    return entries


def _load_competitions(
    raw_list: list[dict[str, Any]], warnings: list[str]
) -> list[Competition]:
    competitions: list[Competition] = []
    for raw in raw_list:
        competition_id = _parse_uuid(raw.get("id"), warnings, "competition.id")
        if competition_id is None:
            continue
        competitions.append(
            Competition(
                id=competition_id,
                name=str(raw.get("name", "")),
                judge_ids=_parse_uuid_list(
                    raw.get("judge_ids", []), warnings, "judge_ids"
                ),
                entry_ids=_parse_uuid_list(
                    raw.get("entry_ids", []), warnings, "entry_ids"
                ),
                rank_marks=_load_rank_marks(raw.get("rank_marks", []), warnings),
                results=None,
                is_obsolete=bool(raw.get("is_obsolete", False)),
            )
        )
    return competitions


def _load_rank_marks(
    raw_list: list[dict[str, Any]], warnings: list[str]
) -> list[RankMark]:
    marks: list[RankMark] = []
    for raw in raw_list:
        judge_id = _parse_uuid(raw.get("judge_id"), warnings, "rank_mark.judge_id")
        entry_id = _parse_uuid(raw.get("entry_id"), warnings, "rank_mark.entry_id")
        if judge_id is None or entry_id is None:
            continue
        marks.append(
            RankMark(
                judge_id=judge_id,
                entry_id=entry_id,
                rank=int(raw.get("rank", 0)),
                notes=raw.get("notes"),
            )
        )
    return marks


def _dump_event(event: Event) -> dict[str, Any]:
    return {
        "id": str(event.id),
        "name": event.name,
        "participants": [
            _dump_participant(participant) for participant in event.participants
        ],
        "entries": [_dump_entry(entry) for entry in event.entries],
        "competitions": [
            _dump_competition(competition) for competition in event.competitions
        ],
        "created_at": _dump_datetime(event.created_at),
        "updated_at": _dump_datetime(event.updated_at),
        "schema_version": event.schema_version,
        "app_version": event.app_version,
    }


def _dump_participant(participant: Participant) -> dict[str, Any]:
    return {
        "id": str(participant.id),
        "number": participant.number,
        "first_name": participant.first_name,
        "last_name": participant.last_name,
        "email": participant.email,
        "is_obsolete": participant.is_obsolete,
    }


def _dump_entry(entry: Entry) -> dict[str, Any]:
    return {
        "id": str(entry.id),
        "name": entry.name,
        "members": [
            {
                "participant_id": str(member.participant_id),
                "role": member.role,
            }
            for member in entry.members
        ],
        "is_obsolete": entry.is_obsolete,
    }


def _dump_competition(competition: Competition) -> dict[str, Any]:
    # reference [S-260210-1.20]
    return {
        "id": str(competition.id),
        "name": competition.name,
        "judge_ids": [str(judge_id) for judge_id in competition.judge_ids],
        "entry_ids": [str(entry_id) for entry_id in competition.entry_ids],
        "rank_marks": [
            {
                "judge_id": str(mark.judge_id),
                "entry_id": str(mark.entry_id),
                "rank": mark.rank,
                "notes": mark.notes,
            }
            for mark in competition.rank_marks
        ],
        "is_obsolete": competition.is_obsolete,
    }


def _parse_uuid(value: Any, warnings: list[str], context: str) -> UUID | None:
    if value is None:
        warnings.append(f"Missing UUID for {context}.")
        return None
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        warnings.append(f"Invalid UUID for {context}: {value}.")
        return None


def _parse_uuid_list(
    values: list[Any], warnings: list[str], context: str
) -> list[UUID]:
    parsed: list[UUID] = []
    for value in values:
        parsed_value = _parse_uuid(value, warnings, context)
        if parsed_value is not None:
            parsed.append(parsed_value)
    return parsed


def _parse_datetime(value: Any, warnings: list[str], context: str) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        warnings.append(f"Invalid datetime for {context}: {value}.")
        return None


def _dump_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()
