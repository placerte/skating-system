from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import List
from uuid import uuid4

@dataclass
class Participant:
    id: str
    first_name: str
    last_name: str
    email: str = ""

    @staticmethod
    def new(first_name: str,last_name: str, email: str = "") -> "Participant":
        return Participant(id=str(uuid4()), first_name=first_name.strip(), last_name=last_name.strip(), email=email.strip())

    @property
    def full_name(self)->str:
        return self.first_name + " " + self.last_name

@dataclass
class Event:
    id: str
    title: str
    participants: List[Participant] = field(default_factory=list)

    @staticmethod
    def new(title: str) -> "Event":
        return Event(id=str(uuid4()), title=title.strip(), participants=[])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "participants": [asdict(p) for p in self.participants],
        }

    @staticmethod
    def from_dict(d: dict) -> "Event":
        parts = [Participant(**p) for p in d.get("participants", [])]
        return Event(id=d["id"], title=d["title"], participants=parts)
