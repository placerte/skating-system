from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Static

from skating_system.domain.models import EntryMember, Participant
from skating_system.services import event_service
from skating_system.ui.modals.text_prompt import TextPrompt
from skating_system.ui.widgets.typeahead_select import TypeaheadSelect


@dataclass(frozen=True)
class EntryFormData:
    name: str
    members: list[EntryMember]


class EntryForm(ModalScreen[EntryFormData | None]):
    """Add/Edit an Entry.

    Uses a typeahead (autocomplete combobox) to add members quickly.
    Display format: "[401] Pierre Lacerte".
    """

    DEFAULT_CSS = """
    EntryForm {
        align: center middle;
    }

    EntryForm > #dialog {
        width: 90%;
        max-width: 100;
        min-width: 60;
        height: 90%;
        max-height: 40;
        padding: 1 2;
        border: round $primary;
        background: $panel;
        overflow-y: auto;
    }

    EntryForm .row {
        height: auto;
        margin-bottom: 1;
    }

    EntryForm #help {
        color: $text-muted;
        height: auto;
        margin-bottom: 1;
    }

    EntryForm #error {
        color: $error;
        height: auto;
        margin-bottom: 1;
    }

    EntryForm #members_table {
        height: 8;
        max-height: 8;
    }

    EntryForm .buttons {
        align-horizontal: right;
        height: auto;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("d", "remove_member", "Remove"),
        ("r", "edit_role", "Role"),
        ("l", "toggle_leader", "Leader"),
    ]

    def __init__(
        self,
        *,
        title: str,
        participants: list[Participant],
        name: str = "",
        members: list[EntryMember] | None = None,
        confirm_label: str = "Save",
    ) -> None:
        super().__init__()
        self._title = title
        self._participants = list(participants)
        self._search_participants = [p for p in self._participants if not p.is_obsolete]
        self._name = name
        self._confirm_label = confirm_label
        self._members: list[EntryMember] = list(members or [])

    def compose(self):
        with Vertical(id="dialog"):
            yield Static(self._title, id="title")
            yield Static("", id="error")

            with Vertical(classes="row"):
                yield Static("Entry name (optional)")
                yield Input(self._name, id="name")

            with Vertical(classes="row"):
                yield TypeaheadSelect[Participant](
                    label="Add member (type number or name)",
                    placeholder="Example: 401 or pierre",
                    items=self._search_participants,
                    get_id=lambda p: p.id,
                    get_label=_participant_label,
                    score=_participant_score,
                    id="member_picker",
                )

            with Vertical(classes="row"):
                yield Static("Members (d remove, r role, l leader)")
                yield DataTable(id="members_table")

            with Horizontal(classes="buttons"):
                yield Button(self._confirm_label, id="confirm")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        table = self.query_one("#members_table", DataTable)
        table.add_columns("#", "Name", "Role")
        table.zebra_stripes = True
        self._refresh_members_table()
        self.query_one("#member_picker", TypeaheadSelect).focus_query()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "confirm":
                self._confirm()
            case "cancel":
                self.dismiss(None)

    def on_typeahead_select_selected(self, event: TypeaheadSelect.Selected) -> None:
        if event.widget_id != "member_picker":
            return
        self.query_one("#error", Static).update("")
        self._add_participant_by_id(event.item_id)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_remove_member(self) -> None:
        row = self._selected_member_row()
        if row is None:
            self._set_error("Select a member to remove.")
            return
        self._members.pop(row)
        self._refresh_members_table()

    def action_edit_role(self) -> None:
        row = self._selected_member_row()
        if row is None:
            self._set_error("Select a member to edit role.")
            return
        current = self._members[row].role or ""
        prompt = TextPrompt(
            title="Set role (empty clears)",
            placeholder="Role",
            confirm_label="Set",
            initial_value=current,
            allow_empty=True,
        )
        self.app.push_screen(prompt, lambda value: self._handle_role_result(row, value))

    def action_toggle_leader(self) -> None:
        row = self._selected_member_row()
        if row is None:
            self._set_error("Select a member to toggle Leader.")
            return

        current = self._members[row]
        is_leader = bool(current.role and current.role.strip().lower() == "leader")

        updated: list[EntryMember] = []
        for index, member in enumerate(self._members):
            if member.role and member.role.strip().lower() == "leader":
                member = EntryMember(participant_id=member.participant_id, role=None)
            if index == row and not is_leader:
                member = EntryMember(
                    participant_id=member.participant_id, role="Leader"
                )
            updated.append(member)
        self._members = updated
        self._refresh_members_table()

    def _confirm(self) -> None:
        name = self.query_one("#name", Input).value.strip()
        if not self._members:
            self._set_error("At least one member is required.")
            return
        self.dismiss(EntryFormData(name=name, members=list(self._members)))

    def _add_participant_by_id(self, participant_id: UUID) -> None:
        if any(member.participant_id == participant_id for member in self._members):
            self._set_error("Participant already in the entry.")
            return

        self._members.append(EntryMember(participant_id=participant_id, role=None))
        self._refresh_members_table()
        picker = self.query_one("#member_picker", TypeaheadSelect)
        picker.clear_query()
        picker.focus_query()

    def _refresh_members_table(self) -> None:
        table = self.query_one("#members_table", DataTable)
        table.clear()
        by_id = {p.id: p for p in self._participants}
        for member in self._members:
            participant = by_id.get(member.participant_id)
            if participant is None:
                continue
            table.add_row(
                str(participant.number),
                _participant_label(participant),
                member.role or "",
            )

    def _selected_member_row(self) -> int | None:
        table = self.query_one("#members_table", DataTable)
        row = table.cursor_row
        if row is None:
            return None
        if row < 0 or row >= len(self._members):
            return None
        return row

    def _handle_role_result(self, row: int, value: str | None) -> None:
        if value is None:
            return
        role = value.strip() or None

        if role and role.lower() == "leader":
            updated: list[EntryMember] = []
            for index, member in enumerate(self._members):
                if member.role and member.role.strip().lower() == "leader":
                    member = EntryMember(
                        participant_id=member.participant_id, role=None
                    )
                if index == row:
                    member = EntryMember(
                        participant_id=member.participant_id, role="Leader"
                    )
                updated.append(member)
            self._members = updated
        else:
            member = self._members[row]
            self._members[row] = EntryMember(
                participant_id=member.participant_id, role=role
            )

        self._refresh_members_table()

    def _set_error(self, message: str) -> None:
        self.query_one("#error", Static).update(message)


def _participant_label(participant: Participant) -> str:
    return f"[{participant.number}] {participant.first_name} {participant.last_name}"


def _participant_score(query: str, participant: Participant) -> int | None:
    if not query:
        return 0

    if query[0].isdigit():
        digits = ""
        for ch in query:
            if ch.isdigit():
                digits += ch
            else:
                break

        num = str(participant.number)
        if num == digits:
            return 1_000_000
        if num.startswith(digits):
            return 900_000 - (participant.number % 10)
        return None

    return event_service.fuzzy_match_score(query, _participant_label(participant))
