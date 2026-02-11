from __future__ import annotations

from pathlib import Path
from typing import Protocol
from uuid import UUID

from skating_system.domain.models import Event
from skating_system.services.skating_scorer import SolveResult


class AppState(Protocol):
    event: Event | None
    file_path: Path | None
    default_dir: Path
    last_warnings: list[str]

    def load_event(self, file_path: Path) -> list[str]: ...

    def save_event(self, file_path: Path | None = None) -> list[str]: ...

    def commit_change(self) -> list[str]: ...

    def mark_dirty(self) -> None: ...

    def set_competition_result(
        self, competition_id: UUID, result: SolveResult
    ) -> None: ...

    def mark_competition_stale(self, competition_id: UUID) -> None: ...

    def competition_is_stale(self, competition_id: UUID) -> bool: ...

    def get_competition_result(self, competition_id: UUID) -> SolveResult | None: ...
