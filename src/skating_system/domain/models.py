from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


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
class Competition:
    id: UUID
    name: str
    judge_ids: list[UUID] = field(default_factory=list)
    entry_ids: list[UUID] = field(default_factory=list)
    rank_marks: list[RankMark] = field(default_factory=list)
