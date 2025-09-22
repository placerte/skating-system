from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional
from domain.models import Event, Participant

class JsonEventRepo:
    def __init__(self, file_path: Path, default_title: str = "My Event"):
        self.file_path = file_path
        self._event: Event | None = None
        self._default_title = default_title

    def load(self) -> Event:
        if self._event:
            return self._event
        if not self.file_path.exists():
            self._event = Event.new(self._default_title)
            self.save(self._event)
            return self._event
        with self.file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self._event = Event.from_dict(data)
        return self._event

    def save(self, event: Event) -> None:
        self._event = event
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(event.to_dict(), f, ensure_ascii=False, indent=2)

    # convenience ops used by the service
    def add_participant(self, p: Participant) -> None:
        ev = self.load()
        ev.participants.append(p)
        self.save(ev)

    def remove_participant(self, participant_id: str) -> None:
        ev = self.load()
        ev.participants = [x for x in ev.participants if x.id != participant_id]
        self.save(ev)

    def list_participants(self) -> List[Participant]:
        return self.load().participants[:]

    def find_participant(self, participant_id: str) -> Optional[Participant]:
        return next((p for p in self.load().participants if p.id == participant_id), None)
