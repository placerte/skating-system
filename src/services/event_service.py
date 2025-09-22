from __future__ import annotations
from typing import List
from domain.models import Participant, Event
from persistence.repo_port import EventRepo

class EventService:
    def __init__(self, repo: EventRepo):
        self.repo = repo

    def get_event(self) -> Event:
        return self.repo.load()

    def add_participant(self, first_name: str, last_name:str, email: str = "") -> Participant:
        if not first_name.strip() and not last_name.strip():
            raise ValueError("Name is required.")
        p = Participant.new(first_name=first_name, last_name=last_name, email=email)
        self.repo.add_participant(p)
        return p

    def remove_participant(self, participant_id: str) -> None:
        self.repo.remove_participant(participant_id)

    def list_participants(self) -> List[Participant]:
        return self.repo.list_participants()

    def rename_event(self, new_title: str) -> None:
        ev = self.repo.load()
        ev.title = new_title.strip() or ev.title
        self.repo.save(ev)
