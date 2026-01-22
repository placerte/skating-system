from __future__ import annotations

from pathlib import Path
from typing import Protocol

from skating_system.domain.models import Event


class EventRepo(Protocol):
    def load_event(self, file_path: Path) -> tuple[Event, list[str]]: ...

    def save_event(self, file_path: Path, event: Event) -> list[str]: ...
