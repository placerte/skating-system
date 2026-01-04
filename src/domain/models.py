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
    title: str
    participants: list[Participant] = field(default_factory=list)

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

@dataclass
class Group:
    id: str
    name: str
    type: str
    obsolete: bool = False

    @staticmethod
    def new(name: str, type:str) -> "Group":
        return Group(
            id=str(uuid4()),
            name=name,
            type=type)
        
@dataclass
class GroupMember:
    id: str
    group_id: str
    participant_id: str
    role: str
    obsolete: bool = False
    
    @staticmethod
    def new(group_id:str, participant_id: str, role: str) -> "GroupMember":
        return GroupMember(
            id=str(uuid4()),
            group_id=group_id,
            participant_id=participant_id,
            role=role)
