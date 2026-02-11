from __future__ import annotations

from uuid import UUID

from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from skating_system.services import event_service
from skating_system.ui.modals.participant_form import (
    ParticipantForm,
    ParticipantFormData,
)
from skating_system.ui.modals.text_prompt import TextPrompt


class ParticipantsScreen(Screen[None]):
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
        self._visible_participant_ids: list[UUID] = []

    def compose(self):
        yield Static("Participants", id="title")
        yield Static("", id="event-info")
        yield Static("", id="filters")
        yield DataTable(id="participants")
        yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#participants", DataTable)
        table.add_columns("#", "First", "Last", "Email", "Obsolete")
        table.zebra_stripes = True

    def on_show(self) -> None:
        self._refresh_event_info()
        self._refresh_table()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_add(self) -> None:
        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event loaded.")
            return

        form = ParticipantForm(title="Add participant", confirm_label="Add")
        self.app.push_screen(form, self._handle_add_result)

    def action_edit(self) -> None:
        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event loaded.")
            return

        participant_id = self._selected_participant_id()
        if participant_id is None:
            self._set_status("Select a participant to edit.")
            return

        participant = event_service.find_participant(event, participant_id)
        if participant is None:
            self._set_status("Selected participant no longer exists.")
            self._refresh_table()
            return

        form = ParticipantForm(
            title=f"Edit participant {participant.number}",
            first_name=participant.first_name,
            last_name=participant.last_name,
            email=participant.email,
            confirm_label="Save",
        )
        self.app.push_screen(
            form,
            lambda data: self._handle_edit_result(participant_id, data),
        )

    def action_toggle_obsolete(self) -> None:
        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event loaded.")
            return

        participant_id = self._selected_participant_id()
        if participant_id is None:
            self._set_status("Select a participant to obsolete/unobsolete.")
            return

        ok = event_service.toggle_participant_obsolete(event, participant_id)
        if not ok:
            self._set_status("Selected participant no longer exists.")
            self._refresh_table()
            return

        participant = event_service.find_participant(event, participant_id)
        if participant is not None:
            state = "Obsolete" if participant.is_obsolete else "Active"
            self._set_status(f"Participant {participant.number} set to {state}.")

        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))

        self._refresh_table()

    def action_search(self) -> None:
        prompt = TextPrompt(
            title="Search participants",
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
        event = getattr(self.app, "event", None)
        if event:
            info = f"Event: {event.name}"
        else:
            info = "Event: None"
        self.query_one("#event-info", Static).update(info)

    def _refresh_table(self) -> None:
        table = self.query_one("#participants", DataTable)
        table.clear()
        self._visible_participant_ids = []

        event = getattr(self.app, "event", None)
        if event is None:
            self.query_one("#filters", Static).update("")
            return

        participants = event_service.search_participants(event, self._query)
        if not self._show_obsolete:
            participants = [p for p in participants if not p.is_obsolete]

        query_text = self._query or "(none)"
        self.query_one("#filters", Static).update(
            f"Search: {query_text} | Show obsolete: {self._show_obsolete}"
        )

        for participant in participants:
            self._visible_participant_ids.append(participant.id)
            table.add_row(
                str(participant.number),
                participant.first_name,
                participant.last_name,
                participant.email or "",
                "yes" if participant.is_obsolete else "",
            )

        # DataTable will keep a cursor once the user interacts.

    def _selected_participant_id(self) -> UUID | None:
        table = self.query_one("#participants", DataTable)
        row = table.cursor_row
        if row is None:
            return None
        if row < 0 or row >= len(self._visible_participant_ids):
            return None
        return self._visible_participant_ids[row]

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _handle_add_result(self, data: ParticipantFormData | None) -> None:
        if data is None:
            self._set_status("Add cancelled.")
            return

        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event loaded.")
            return

        participant = event_service.add_participant(
            event,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
        )
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status(f"Added participant {participant.number}.")
        self._refresh_table()

    def _handle_edit_result(
        self,
        participant_id: UUID,
        data: ParticipantFormData | None,
    ) -> None:
        if data is None:
            self._set_status("Edit cancelled.")
            return

        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event loaded.")
            return

        participant = event_service.update_participant(
            event,
            participant_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
        )
        if participant is None:
            self._set_status("Selected participant no longer exists.")
            self._refresh_table()
            return

        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status(f"Updated participant {participant.number}.")
        self._refresh_table()

    def _handle_search_result(self, value: str | None) -> None:
        if value is None:
            return
        self._query = value
        self._refresh_table()

    def _commit_change(self) -> list[str]:
        committer = getattr(self.app, "commit_change", None)
        if committer is None:
            marker = getattr(self.app, "mark_dirty", None)
            if marker is not None:
                marker()
            return []
        return committer()
