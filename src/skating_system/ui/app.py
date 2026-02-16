from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from textual.app import App

from skating_system.domain.models import Event
from skating_system.persistence.json_repo import JsonEventRepo
from skating_system.services import event_service
from skating_system.services.event_service import create_event
from skating_system.services.ranking_service import compute_results
from skating_system.services.skating_scorer import SolveResult
from skating_system.ui.screens.competitions import CompetitionsScreen


class SkatingApp(App[None]):
    CSS_PATH = None

    def __init__(self) -> None:
        super().__init__()
        self.event: Event | None = None
        self.file_path: Path | None = None
        self.repo = JsonEventRepo()
        self.dirty = False
        self.default_dir = Path.home() / "skating-events"
        self.last_warnings: list[str] = []
        self.solve_cache: dict[UUID, SolveResult] = {}
        self.stale_competitions: set[UUID] = set()
        self.auto_recompute = True
        self._load_last_event()

    def on_mount(self) -> None:
        if self.event is None:
            self.event = create_event("Untitled Event")
        self.push_screen(CompetitionsScreen())

    def new_event(self, name: str) -> None:
        self.event = create_event(name)
        self.file_path = None
        self.dirty = False
        self.last_warnings = []
        self.solve_cache = {}
        self.stale_competitions = set()

    def load_event(self, file_path: Path) -> list[str]:
        try:
            event, warnings = self.repo.load_event(file_path)
        except (ValueError, OSError) as exc:
            warnings = [str(exc)]
            self.last_warnings = warnings
            return warnings

        self.event = event
        self.file_path = file_path
        self.dirty = False
        self.last_warnings = warnings
        self.solve_cache = {}
        self.stale_competitions = set()
        # reference [S-260210-1.21]
        if self.auto_recompute:
            self._recompute_loaded_event()
        self._store_last_event(file_path)
        return warnings

    def save_event(self, file_path: Path | None = None) -> list[str]:
        if self.event is None:
            warnings = ["No event is loaded."]
            self.last_warnings = warnings
            return warnings

        target_path = file_path or self.file_path
        if target_path is None:
            warnings = ["No file path selected."]
            self.last_warnings = warnings
            return warnings

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            warnings = self.repo.save_event(target_path, self.event)
        except OSError as exc:
            warnings = [str(exc)]
            self.last_warnings = warnings
            self.dirty = True
            return warnings

        self.file_path = target_path
        self.dirty = False
        self.last_warnings = warnings
        self._store_last_event(target_path)
        return warnings

    def set_competition_result(self, competition_id: UUID, result: SolveResult) -> None:
        self.solve_cache[competition_id] = result
        self.stale_competitions.discard(competition_id)

    def mark_competition_stale(self, competition_id: UUID) -> None:
        self.stale_competitions.add(competition_id)

    def competition_is_stale(self, competition_id: UUID) -> bool:
        return competition_id in self.stale_competitions

    def get_competition_result(self, competition_id: UUID) -> SolveResult | None:
        return self.solve_cache.get(competition_id)

    def mark_dirty(self) -> None:
        self.dirty = True

    def commit_change(self) -> list[str]:
        """Mark the event dirty, and auto-save if a file path exists."""

        self.dirty = True
        if self.file_path is None:
            return []
        return self.save_event(self.file_path)

    def _load_last_event(self) -> None:
        config_path = self._config_path()
        if not config_path.exists():
            return
        try:
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        last_path = raw.get("last_event_path")
        if not last_path:
            return
        path = Path(last_path)
        if not path.exists():
            return
        self.load_event(path)

    def _recompute_loaded_event(self) -> None:
        if self.event is None:
            return
        entry_labels = self._entry_label_lookup(self.event)
        for competition in self.event.competitions:
            result, errors = compute_results(competition, entry_labels=entry_labels)
            if errors or result is None:
                self.stale_competitions.add(competition.id)
                continue
            self.solve_cache[competition.id] = result

    def _entry_label_lookup(self, event: Event) -> dict[UUID, str]:
        participant_lookup = {p.id: p for p in event.participants}
        return {
            entry.id: event_service.entry_display_label(entry, participant_lookup)
            for entry in event.entries
        }

    def _store_last_event(self, file_path: Path) -> None:
        config_path = self._config_path()
        try:
            config_path.write_text(
                json.dumps({"last_event_path": str(file_path)}, indent=2),
                encoding="utf-8",
            )
        except OSError:
            return

    def _config_path(self) -> Path:
        return Path.home() / ".skating_system.json"


def run() -> None:
    SkatingApp().run()
