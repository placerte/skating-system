from __future__ import annotations

from typing import cast
from uuid import UUID

from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from skating_system.domain.models import EntryMember, Participant
from skating_system.services import event_service
from skating_system.ui.modals.entry_form import EntryForm, EntryFormData
from skating_system.ui.modals.text_prompt import TextPrompt
from skating_system.ui.app_state import AppState


class EntriesScreen(Screen[None]):
    BINDINGS = [
        ("a", "add", "Add"),
        ("e", "edit", "Edit"),
        ("o", "toggle_obsolete", "Obsolete"),
        ("/", "search", "Search"),
        ("t", "toggle_show_obsolete", "Show obsolete"),
        ("escape", "back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._query = ""
        self._show_obsolete = False
        self._visible_entry_ids: list[UUID] = []

    def compose(self):
        yield Static("Entries", id="title")
        yield Static("", id="event-info")
        yield Static("", id="filters")
        yield DataTable(id="entries")
        yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#entries", DataTable)
        table.add_columns("Label", "Members", "Obsolete")
        table.zebra_stripes = True

    def on_show(self) -> None:
        self._refresh_event_info()
        self._refresh_table()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_add(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        active_participants = [p for p in event.participants if not p.is_obsolete]
        if not active_participants:
            self._set_status("Add participants first.")
            return

        form = EntryForm(
            title="Add entry",
            participants=list(event.participants),
            confirm_label="Add",
        )
        self.app.push_screen(form, self._handle_add_result)

    def action_edit(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        entry_id = self._selected_entry_id()
        if entry_id is None:
            self._set_status("Select an entry to edit.")
            return

        entry = event_service.find_entry(event, entry_id)
        if entry is None:
            self._set_status("Selected entry no longer exists.")
            self._refresh_table()
            return

        form = EntryForm(
            title="Edit entry",
            participants=list(event.participants),
            name=entry.name,
            members=list(entry.members),
            confirm_label="Save",
        )
        self.app.push_screen(
            form, lambda data: self._handle_edit_result(entry_id, data)
        )

    def action_toggle_obsolete(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        entry_id = self._selected_entry_id()
        if entry_id is None:
            self._set_status("Select an entry to obsolete/unobsolete.")
            return

        ok = event_service.toggle_entry_obsolete(event, entry_id)
        if not ok:
            self._set_status("Selected entry no longer exists.")
            self._refresh_table()
            return

        entry = event_service.find_entry(event, entry_id)
        if entry is not None:
            state = "Obsolete" if entry.is_obsolete else "Active"
            self._set_status(f"Entry set to {state}.")

        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))

        self._refresh_table()

    def action_search(self) -> None:
        prompt = TextPrompt(
            title="Search entries",
            placeholder="Search…",
            confirm_label="Search",
            initial_value=self._query,
            allow_empty=True,
        )
        self.app.push_screen(prompt, self._handle_search_result)

    def action_toggle_show_obsolete(self) -> None:
        self._show_obsolete = not self._show_obsolete
        self._refresh_table()

    def _refresh_event_info(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
        if event:
            info = f"Event: {event.name}"
        else:
            info = "Event: None"
        self.query_one("#event-info", Static).update(info)

    def _refresh_table(self) -> None:
        table = self.query_one("#entries", DataTable)
        table.clear()
        self._visible_entry_ids = []

        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self.query_one("#filters", Static).update("")
            return

        participant_lookup = {p.id: p for p in event.participants}
        entries = event_service.search_entries(event, self._query, participant_lookup)
        if not self._show_obsolete:
            entries = [e for e in entries if not e.is_obsolete]

        query_text = self._query or "(none)"
        self.query_one("#filters", Static).update(
            f"Search: {query_text} | Show obsolete: {self._show_obsolete}"
        )

        for entry in entries:
            self._visible_entry_ids.append(entry.id)
            label = event_service.entry_display_label(entry, participant_lookup)
            members = _members_summary(entry.members, participant_lookup)
            table.add_row(
                label,
                members,
                "yes" if entry.is_obsolete else "",
            )

    def _selected_entry_id(self) -> UUID | None:
        table = self.query_one("#entries", DataTable)
        row = table.cursor_row
        if row is None:
            return None
        if row < 0 or row >= len(self._visible_entry_ids):
            return None
        return self._visible_entry_ids[row]

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _handle_add_result(self, data: EntryFormData | None) -> None:
        if data is None:
            self._set_status("Add cancelled.")
            return

        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        event_service.add_entry(event, name=data.name, members=data.members)
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Entry added.")
        self._refresh_table()

    def _handle_edit_result(self, entry_id: UUID, data: EntryFormData | None) -> None:
        if data is None:
            self._set_status("Edit cancelled.")
            return

        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        entry = event_service.update_entry(
            event, entry_id, name=data.name, members=data.members
        )
        if entry is None:
            self._set_status("Selected entry no longer exists.")
            self._refresh_table()
            return

        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Entry updated.")
        self._refresh_table()

    def _handle_search_result(self, value: str | None) -> None:
        if value is None:
            return
        self._query = value
        self._refresh_table()

    def _commit_change(self) -> list[str]:
        app = cast(AppState, self.app)
        app.mark_dirty()
        return app.commit_change()


def _members_summary(
    members: list[EntryMember],
    participant_lookup: dict[UUID, Participant],
) -> str:
    labels: list[str] = []
    for member in members:
        participant = participant_lookup.get(member.participant_id)
        if participant is None:
            continue
        labels.append(str(participant.number))
    return ", ".join(labels)
