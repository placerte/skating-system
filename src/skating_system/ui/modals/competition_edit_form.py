from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static

from skating_system.domain.models import Entry, EntryMember, Participant
from skating_system.services import event_service
from skating_system.ui.widgets.typeahead_select import TypeaheadSelect


@dataclass(frozen=True)
class CompetitionEditFormData:
    judge_ids: list[UUID]
    entry_ids: list[UUID]


class CompetitionEditForm(ModalScreen[CompetitionEditFormData | None]):
    """Edit competition judges and entries.

    Uses typeahead / autocomplete combobox workflow.
    """

    DEFAULT_CSS = """
    CompetitionEditForm {
        align: center middle;
    }

    CompetitionEditForm > #dialog {
        width: 96%;
        max-width: 110;
        min-width: 70;
        height: auto;
        padding: 1 2;
        border: round $primary;
        background: $panel;
    }

    CompetitionEditForm .row {
        height: auto;
        margin-bottom: 1;
    }

    CompetitionEditForm #error {
        color: $error;
        height: auto;
        margin-bottom: 1;
    }

    CompetitionEditForm .panes {
        height: auto;
        margin-bottom: 1;
    }

    CompetitionEditForm .buttons {
        align-horizontal: right;
        height: auto;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "confirm", "Save"),
        ("d", "remove_selected", "Remove"),
        ("tab", "focus_next", "Next"),
        ("shift+tab", "focus_previous", "Prev"),
    ]

    def __init__(
        self,
        *,
        title: str,
        participants: list[Participant],
        entries: list[Entry],
        judge_ids: list[UUID] | None = None,
        entry_ids: list[UUID] | None = None,
        confirm_label: str = "Save",
    ) -> None:
        super().__init__()
        self._title = title
        self._participants = list(participants)
        self._entries = list(entries)
        self._confirm_label = confirm_label

        self._participant_lookup = {p.id: p for p in self._participants}

        self._judge_ids: list[UUID] = list(judge_ids or [])
        self._entry_ids: list[UUID] = list(entry_ids or [])

    def compose(self):
        with Vertical(id="dialog"):
            yield Static(self._title, id="title")
            yield Static("", id="error")

            with Horizontal(classes="panes"):
                with Vertical(id="judges_pane"):
                    yield TypeaheadSelect[Participant](
                        label="Add judge",
                        placeholder="Type a number or name…",
                        items=[p for p in self._participants if not p.is_obsolete],
                        get_id=lambda p: p.id,
                        get_label=_participant_label,
                        score=_participant_score,
                        id="judge_picker",
                    )
                    yield Static("Selected judges (d remove)")
                    yield DataTable(id="selected_judges")

                with Vertical(id="entries_pane"):
                    yield TypeaheadSelect[Entry](
                        label="Add entry",
                        placeholder="Type entry name / number…",
                        items=[e for e in self._entries if not e.is_obsolete],
                        get_id=lambda e: e.id,
                        get_label=lambda e: _entry_label(e, self._participant_lookup),
                        score=lambda q, e: _entry_score(q, e, self._participant_lookup),
                        id="entry_picker",
                    )
                    yield Static("Selected entries (d remove)")
                    yield DataTable(id="selected_entries")

            with Horizontal(classes="buttons"):
                yield Button(self._confirm_label, id="confirm")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        judges = self.query_one("#selected_judges", DataTable)
        judges.add_columns("#", "Name")
        judges.zebra_stripes = True

        entries = self.query_one("#selected_entries", DataTable)
        entries.add_columns("Label")
        entries.zebra_stripes = True

        self._refresh_selected_tables()
        self.query_one("#judge_picker", TypeaheadSelect).focus_query()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "confirm":
                self._confirm()
            case "cancel":
                self.dismiss(None)

    def on_typeahead_select_selected(self, event: Any) -> None:
        if event.widget_id == "judge_picker":
            self._add_judge(event.item_id)
            picker = self.query_one("#judge_picker", TypeaheadSelect)
            picker.clear_query()
            picker.focus_query()
        elif event.widget_id == "entry_picker":
            self._add_entry(event.item_id)
            picker = self.query_one("#entry_picker", TypeaheadSelect)
            picker.clear_query()
            picker.focus_query()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_confirm(self) -> None:
        self._confirm()

    def action_remove_selected(self) -> None:
        focused = self.focused
        if not isinstance(focused, DataTable):
            return

        row = focused.cursor_row
        if row is None:
            return

        if focused.id == "selected_judges":
            if 0 <= row < len(self._judge_ids):
                self._judge_ids.pop(row)
                self._refresh_selected_tables()
        elif focused.id == "selected_entries":
            if 0 <= row < len(self._entry_ids):
                self._entry_ids.pop(row)
                self._refresh_selected_tables()

    def _add_judge(self, participant_id: UUID) -> None:
        if participant_id in self._judge_ids:
            self._set_error("Judge already selected.")
            return
        self._judge_ids.append(participant_id)
        self._set_error("")
        self._refresh_selected_tables()

    def _add_entry(self, entry_id: UUID) -> None:
        if entry_id in self._entry_ids:
            self._set_error("Entry already selected.")
            return
        self._entry_ids.append(entry_id)
        self._set_error("")
        self._refresh_selected_tables()

    def _refresh_selected_tables(self) -> None:
        judges = self.query_one("#selected_judges", DataTable)
        judges.clear()
        for judge_id in self._judge_ids:
            participant = self._participant_lookup.get(judge_id)
            if participant is None:
                continue
            judges.add_row(str(participant.number), _participant_label(participant))

        entry_lookup = {e.id: e for e in self._entries}
        entries = self.query_one("#selected_entries", DataTable)
        entries.clear()
        for entry_id in self._entry_ids:
            entry = entry_lookup.get(entry_id)
            if entry is None:
                continue
            entries.add_row(_entry_label(entry, self._participant_lookup))

    def _confirm(self) -> None:
        if not self._judge_ids:
            self._set_error("Select at least one judge.")
            return
        if len(self._entry_ids) < 2:
            self._set_error("Select at least two entries.")
            return

        self.dismiss(
            CompetitionEditFormData(
                judge_ids=list(self._judge_ids),
                entry_ids=list(self._entry_ids),
            )
        )

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


def _entry_label(entry: Entry, participant_lookup: dict[UUID, Participant]) -> str:
    return event_service.entry_display_label(entry, participant_lookup)


def _entry_score(
    query: str,
    entry: Entry,
    participant_lookup: dict[UUID, Participant],
) -> int | None:
    if not query:
        return 0

    label = _entry_label(entry, participant_lookup)
    member_numbers = _member_numbers(entry.members, participant_lookup)
    search_text = f"{label} {member_numbers}".strip()

    if query[0].isdigit():
        digits = ""
        for ch in query:
            if ch.isdigit():
                digits += ch
            else:
                break
        for number in member_numbers.split():
            if number == digits:
                return 1_000_000
            if number.startswith(digits):
                return 900_000

    return event_service.fuzzy_match_score(query, search_text)


def _member_numbers(
    members: list[EntryMember], participant_lookup: dict[UUID, Participant]
) -> str:
    numbers: list[str] = []
    for member in members:
        participant = participant_lookup.get(member.participant_id)
        if participant is None:
            continue
        numbers.append(str(participant.number))
    return " ".join(numbers)
