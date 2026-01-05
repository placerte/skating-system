from __future__ import annotations
from dataclasses import dataclass, asdict, field
from uuid import uuid4


@dataclass
class Participant:
    id: str
    first_name: str
    last_name: str
    number: int
    email: str = ""
    obsolete: bool = False

    @staticmethod
    def new(
        first_name: str, last_name: str, email: str = "", number: int = -1
    ) -> "Participant":
        return Participant(
            id = str(uuid4()),
            first_name = first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip(),
            number=number,
        )

    @property
    def full_name(self) -> str:
        return self.first_name + " " + self.last_name


@dataclass
class Event:
    id: str
    name: str
    participants: list[Participant] = field(default_factory=list)
    competitors: list[Competitor] = field(default_factory=list)
    competitor_groups: list[CompetitorGroup] = field(default_factory=list)
    competitions: list[Competition] = field(default_factory=list)

    @staticmethod
    def new(name: str) -> "Event":
        return Event(id=str(uuid4()), name=name.strip(), participants=[])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "participants": [asdict(p) for p in self.participants],
            "competitors": [asdict(c) for c in self.competitors],
            "competitor_groups": [asdict(c) for c in self.competitor_groups],
            "competitions": [asdict(c) for c in self.competitions],
        }

    @staticmethod
    def from_dict(d: dict) -> "Event":
        parts = [Participant(**p) for p in d.get("participants", [])]
        return Event(id=d["id"], name=d["name"], participants=parts)

@dataclass
class CompetitorGroup:
    id: str
    name: str
    type: str
    competitor_ids: list[str] = []
    obsolete: bool = False

    @staticmethod
    def new(name: str, type:str) -> "CompetitorGroup":
        return CompetitorGroup(
            id=str(uuid4()),
            name=name,
            type=type)
        
@dataclass
class Competitor:
    id: str
    participant_id: str
    role: str
    obsolete: bool = False
    
    @staticmethod
    def new(participant_id: str, role: str) -> "Competitor":
        return Competitor(
            id=str(uuid4()),
            participant_id=participant_id,
            role=role)

@dataclass
class Competition:
    id: str
    name: str
    obsolete: bool = False
    scores: list[Score] = field(default_factory=list)
    competitor_group_ids: list[str] = field(default_factory=list)
    judges_ids: list[str] = field(default_factory=list)

    @staticmethod
    def new(name: str) -> "Competition":
        return Competition(
            id=str(uuid4()),
            name=name)

@dataclass
class Score:
    id: str
    value: int
    judge_id: str
    competitor_group_id: str
    obsolete: bool = False

    @staticmethod
    def new(value: int, judge_id: str, competitor_group_id: str) -> "Score":
        return Score(
            id=str(uuid4()),
            value=value,
            judge_id=judge_id,
            competitor_group_id=competitor_group_id
        )

