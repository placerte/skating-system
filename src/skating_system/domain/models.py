from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Participant:
    id: UUID
    number: int
    first_name: str
    last_name: str
    email: str | None = None
    is_obsolete: bool = False


@dataclass
class EntryMember:
    participant_id: UUID
    role: str | None = None


@dataclass
class Entry:
    id: UUID
    name: str
    members: list[EntryMember] = field(default_factory=list)
    is_obsolete: bool = False


@dataclass
class RankMark:
    judge_id: UUID
    entry_id: UUID
    rank: int
    notes: str | None = None


@dataclass
class Placement:
    entry_id: UUID
    final_place: float
    rule_trace: str = ""


@dataclass
class CompetitionResults:
    placements: list[Placement] = field(default_factory=list)
    is_provisional: bool = False


@dataclass
class Competition:
    id: UUID
    name: str
    judge_ids: list[UUID] = field(default_factory=list)
    entry_ids: list[UUID] = field(default_factory=list)
    rank_marks: list[RankMark] = field(default_factory=list)
    results: CompetitionResults | None = None


@dataclass
class Event:
    id: UUID
    name: str
    participants: list[Participant] = field(default_factory=list)
    entries: list[Entry] = field(default_factory=list)
    competitions: list[Competition] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    schema_version: int | None = None
    app_version: str | None = None
