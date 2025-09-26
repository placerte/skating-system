from __future__ import annotations
from typing import List, Optional
from domain.models import Participant, Event
from persistence.repo_port import EventRepo


class EventService:
    def __init__(self, repo: EventRepo):
        self.repo = repo

    def get_event(self) -> Event:
        return self.repo.load()

    def add_participant(
        self, first_name: str, last_name: str, email: str = ""
    ) -> Participant:
        if not first_name.strip() and not last_name.strip():
            raise ValueError("Name is required.")
        number = self.get_next_participant_number()
        p = Participant.new(
            first_name=first_name, last_name=last_name, email=email, number=number
        )
        self.repo.add_participant(p)
        return p

    def remove_participant(self, participant_id: str) -> None:
        self.repo.remove_participant(participant_id)

    def list_participants(self, include_obsolete: bool = False) -> list[Participant]:
        all_participants: list[Participant] = self.repo.list_participants()
        if include_obsolete:
            return all_participants
        else:
            active_participants: list[Participant] = []
            for participant in all_participants:
                if not participant.obsolete:
                    active_participants.append(participant)
            return active_participants

    def get_next_participant_number(self, min_number: int = 100) -> int:
        next_number: int = min_number
        participant: Optional[Participant]
        max_number: int = 1000000
        while next_number <= max_number:
            participant = self.get_participant_by_number(next_number)
            if participant is not None:
                next_number += 1
            else:
                return next_number

        return max_number

    def get_participant_by_number(self, number: int) -> Optional[Participant]:
        participants = self.list_participants(include_obsolete=True)
        participant: Optional[Participant] = None

        for p in participants:
            if p.number == number:
                participant = p

        return participant

    def rename_event(self, new_title: str) -> None:
        ev = self.repo.load()
        ev.title = new_title.strip() or ev.title
        self.repo.save(ev)
