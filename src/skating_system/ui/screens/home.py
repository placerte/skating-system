from __future__ import annotations

from pathlib import Path

from textual.screen import Screen
from textual.widgets import Footer, Static

from skating_system.ui.screens.competitions import CompetitionsScreen
from skating_system.ui.screens.entries import EntriesScreen
from skating_system.ui.screens.participants import ParticipantsScreen
from skating_system.ui.modals.text_prompt import TextPrompt


class HomeScreen(Screen[None]):
    BINDINGS = [
        ("p", "go_participants", "Participants"),
        ("e", "go_entries", "Entries"),
        ("c", "go_competitions", "Competitions"),
        ("l", "load_event", "Load"),
        ("s", "save_event", "Save"),
        ("r", "rename_event", "Rename"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def compose(self):
        yield Static("Skating System", id="title")
        yield Static("", id="event-info")
        yield Static("", id="default-dir")
        yield Static("", id="status")
        yield Footer()

    def on_show(self) -> None:
        self._refresh_event_info()
        self._set_status_from_app()

    def action_go_participants(self) -> None:
        self.app.push_screen(ParticipantsScreen())

    def action_go_entries(self) -> None:
        self.app.push_screen(EntriesScreen())

    def action_go_competitions(self) -> None:
        self.app.push_screen(CompetitionsScreen())

    def action_load_event(self) -> None:
        default_dir = getattr(self.app, "default_dir", Path.home())
        initial = getattr(self.app, "file_path", None)
        initial_value = str(initial) if initial else str(default_dir / "event.json")
        prompt = TextPrompt(
            title="Load event",
            placeholder="Event file path",
            confirm_label="Load",
            initial_value=initial_value,
        )
        self.app.push_screen(prompt, self._handle_load_prompt)

    def action_save_event(self) -> None:
        default_dir = getattr(self.app, "default_dir", Path.home())
        initial = getattr(self.app, "file_path", None)
        initial_value = str(initial) if initial else str(default_dir / "event.json")
        prompt = TextPrompt(
            title="Save event",
            placeholder="Event file path",
            confirm_label="Save",
            initial_value=initial_value,
        )
        self.app.push_screen(prompt, self._handle_save_prompt)

    def action_rename_event(self) -> None:
        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event to rename.")
            return

        prompt = TextPrompt(
            title="Rename event",
            placeholder="Event name",
            confirm_label="Rename",
            initial_value=event.name,
        )
        self.app.push_screen(prompt, self._handle_rename_prompt)

    def action_quit(self) -> None:
        self.app.exit()

    def _refresh_event_info(self) -> None:
        event = getattr(self.app, "event", None)
        file_path = getattr(self.app, "file_path", None)
        event_name = event.name if event else "No event"
        path = str(file_path) if file_path else "No file"
        info = f"Event: {event_name} | File: {path}"
        self.query_one("#event-info", Static).update(info)

        default_dir = getattr(self.app, "default_dir", None)
        if default_dir:
            default_text = f"Default directory: {default_dir}"
        else:
            default_text = "Default directory: None"
        self.query_one("#default-dir", Static).update(default_text)

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _set_status_from_app(self) -> None:
        warnings = getattr(self.app, "last_warnings", [])
        if warnings:
            self._set_status("; ".join(warnings))

    def _handle_rename_prompt(self, name: str | None) -> None:
        if name is None:
            self._set_status("Rename cancelled.")
            return

        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event to rename.")
            return

        event.name = name

        committer = getattr(self.app, "commit_change", None)
        if committer is not None:
            warnings = committer()
        else:
            warnings = []

        file_path = getattr(self.app, "file_path", None)
        if file_path is None:
            self._set_status("Event name updated (not saved yet).")
        elif warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Event name updated (auto-saved).")
        self._refresh_event_info()

    def _handle_load_prompt(self, value: str | None) -> None:
        if value is None:
            self._set_status("Load cancelled.")
            return

        path = self._resolve_path(value)
        if path is None:
            self._set_status("Enter a file path to load.")
            return
        if not path.exists():
            self._set_status("File not found.")
            return

        loader = getattr(self.app, "load_event", None)
        if loader is None:
            self._set_status("Load not available.")
            return
        warnings = loader(path)
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Event loaded.")
        self._refresh_event_info()

    def _handle_save_prompt(self, value: str | None) -> None:
        if value is None:
            self._set_status("Save cancelled.")
            return

        path = self._resolve_path(value)
        if path is None:
            self._set_status("Enter a file path to save.")
            return

        saver = getattr(self.app, "save_event", None)
        if saver is None:
            self._set_status("Save not available.")
            return
        warnings = saver(path)
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Event saved.")
        self._refresh_event_info()

    def _resolve_path(self, raw: str) -> Path | None:
        if not raw:
            return None
        path = Path(raw)
        if not path.is_absolute():
            default_dir = getattr(self.app, "default_dir", None)
            if default_dir:
                path = default_dir / path
        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")
        return path
