from __future__ import annotations

from uuid import UUID

from rich.text import Text
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from skating_system.domain.models import Competition, Entry, Event, Participant
from skating_system.services import event_service
from skating_system.services.ranking_service import compute_and_store_results
from skating_system.ui.modals.text_prompt import TextPrompt
from skating_system.ui.modals.typeahead_picker import TypeaheadPicker


class CompetitionEditScreen(Screen[None]):
    """Competition Edit screen.

    Combined setup (judges/entries) + rank entry + results view.
    """

    DEFAULT_CSS = """
    CompetitionEditScreen {
        layout: horizontal;
    }

    CompetitionEditScreen #main {
        width: 1fr;
    }

    CompetitionEditScreen #sidebar {
        width: 35;
        padding: 1;
        border-left: solid $primary;
    }

    CompetitionEditScreen #empty-overlay {
        height: auto;
        color: $text-muted;
        text-align: center;
        margin-top: 4;
    }
    """

    BINDINGS = [
        ("j", "add_judge", "Add judge"),
        ("e", "add_entry", "Add entry"),
        ("r", "rename", "Rename"),
        ("enter", "edit_cell", "Edit rank"),
        ("c", "clear_cell", "Clear rank"),
        ("C", "compute", "Compute"),
        ("d", "remove", "Remove"),
        ("escape", "back", "Back"),
        ("1", "quick_rank(1)", ""),
        ("2", "quick_rank(2)", ""),
        ("3", "quick_rank(3)", ""),
        ("4", "quick_rank(4)", ""),
        ("5", "quick_rank(5)", ""),
        ("6", "quick_rank(6)", ""),
        ("7", "quick_rank(7)", ""),
        ("8", "quick_rank(8)", ""),
        ("9", "quick_rank(9)", ""),
    ]

    def __init__(self, competition_id: UUID) -> None:
        super().__init__()
        self._competition_id = competition_id
        self._columns_built = False
        self._visible_entry_ids: list[UUID] = []
        self._visible_judge_ids: list[UUID] = []

    def compose(self):
        with Horizontal():
            with Vertical(id="main"):
                yield Static("", id="title")
                yield Static("", id="event-info")
                yield Static("", id="empty-overlay")
                yield DataTable(id="matrix")
                yield Static("", id="status")
                yield Footer()

            with Vertical(id="sidebar"):
                yield Static("Results (provisional)", id="results-title")
                yield Static("", id="results-content")
                yield Static("Press 'C' to compute", id="results-hint")

    def on_mount(self) -> None:
        table = self.query_one("#matrix", DataTable)
        table.add_columns("Entry")
        table.zebra_stripes = True

    def on_show(self) -> None:
        self._refresh_headers()
        self._ensure_judge_columns()
        self._refresh_matrix()
        self._refresh_results()
        self._refresh_empty_overlay()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_add_judge(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        participants = [p for p in event.participants if not p.is_obsolete]
        if not participants:
            self._set_status("Add participants first.")
            return

        picker = TypeaheadPicker[Participant](
            title="Add judge",
            label="",
            placeholder="Type number or name…",
            items=participants,
            get_id=lambda p: p.id,
            get_label=_participant_label,
            score=_participant_score,
        )
        self.app.push_screen(picker, self._handle_add_judge)

    def action_add_entry(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        entries = [e for e in event.entries if not e.is_obsolete]
        if not entries:
            self._set_status("Add entries first.")
            return

        participant_lookup = {p.id: p for p in event.participants}
        picker = TypeaheadPicker[Entry](
            title="Add entry",
            label="",
            placeholder="Type entry name or number…",
            items=entries,
            get_id=lambda e: e.id,
            get_label=lambda e: event_service.entry_display_label(
                e, participant_lookup
            ),
            score=lambda q, e: _entry_score(q, e, participant_lookup),
        )
        self.app.push_screen(picker, self._handle_add_entry)

    def action_rename(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        prompt = TextPrompt(
            title="Rename competition",
            placeholder="Competition name",
            confirm_label="Rename",
            initial_value=competition.name,
        )
        self.app.push_screen(prompt, self._handle_rename)

    def action_edit_cell(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        table = self.query_one("#matrix", DataTable)
        row = table.cursor_row
        col = table.cursor_column
        if row is None or col is None or col == 0:
            self._set_status("Select a judge cell.")
            return

        if row < 0 or row >= len(self._visible_entry_ids):
            return
        if (col - 1) < 0 or (col - 1) >= len(self._visible_judge_ids):
            return

        entry_id = self._visible_entry_ids[row]
        judge_id = self._visible_judge_ids[col - 1]

        existing = _find_mark(competition, judge_id=judge_id, entry_id=entry_id)
        initial = str(existing.rank) if existing else ""

        prompt = TextPrompt(
            title="Set rank (empty clears)",
            placeholder="Rank",
            confirm_label="Set",
            initial_value=initial,
            allow_empty=True,
        )
        self.app.push_screen(
            prompt,
            lambda value: self._handle_rank_input(judge_id, entry_id, value),
        )

    def action_clear_cell(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        table = self.query_one("#matrix", DataTable)
        row = table.cursor_row
        col = table.cursor_column
        if row is None or col is None or col == 0:
            self._set_status("Select a judge cell to clear.")
            return

        if row < 0 or row >= len(self._visible_entry_ids):
            return
        if (col - 1) < 0 or (col - 1) >= len(self._visible_judge_ids):
            return

        entry_id = self._visible_entry_ids[row]
        judge_id = self._visible_judge_ids[col - 1]

        removed = event_service.clear_rank_mark(
            event, self._competition_id, judge_id=judge_id, entry_id=entry_id
        )
        if removed:
            warnings = self._commit_change()
            if warnings:
                self._set_status("; ".join(warnings))
            else:
                self._set_status("Rank cleared.")
        else:
            self._set_status("No rank to clear.")
        self._refresh_matrix()

    def action_compute(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        compute_and_store_results(competition)
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Results computed.")
        self._refresh_results()

    def action_remove(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        table = self.query_one("#matrix", DataTable)
        row = table.cursor_row
        col = table.cursor_column

        if row is not None and col == 0:
            if 0 <= row < len(self._visible_entry_ids):
                entry_id = self._visible_entry_ids[row]
                competition.entry_ids = [
                    eid for eid in competition.entry_ids if eid != entry_id
                ]
                competition.rank_marks = [
                    m for m in competition.rank_marks if m.entry_id != entry_id
                ]
                warnings = self._commit_change()
                if warnings:
                    self._set_status("; ".join(warnings))
                else:
                    self._set_status("Entry removed from competition.")
                self._columns_built = False
                self._refresh_matrix()
                self._refresh_empty_overlay()
                return

        if col is not None and col > 0 and row == 0:
            judge_index = col - 1
            if 0 <= judge_index < len(self._visible_judge_ids):
                judge_id = self._visible_judge_ids[judge_index]
                competition.judge_ids = [
                    jid for jid in competition.judge_ids if jid != judge_id
                ]
                competition.rank_marks = [
                    m for m in competition.rank_marks if m.judge_id != judge_id
                ]
                warnings = self._commit_change()
                if warnings:
                    self._set_status("; ".join(warnings))
                else:
                    self._set_status("Judge removed from competition.")
                self._columns_built = False
                self._refresh_matrix()
                self._refresh_empty_overlay()
                return

        self._set_status("Select a row or column header to remove.")

    def action_quick_rank(self, rank: int) -> None:
        """Quick rank entry: press 1-9 to set rank on selected cell."""
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        table = self.query_one("#matrix", DataTable)
        row = table.cursor_row
        col = table.cursor_column
        if row is None or col is None or col == 0:
            return

        if row < 0 or row >= len(self._visible_entry_ids):
            return
        if (col - 1) < 0 or (col - 1) >= len(self._visible_judge_ids):
            return

        entry_id = self._visible_entry_ids[row]
        judge_id = self._visible_judge_ids[col - 1]

        entry_count = len(competition.entry_ids)
        if rank < 1 or rank > entry_count:
            self._set_status(f"Rank must be between 1 and {entry_count}.")
            return

        # Remember cursor position before refresh
        cursor_row = row
        cursor_col = col

        event_service.set_rank_mark(
            event, self._competition_id, judge_id=judge_id, entry_id=entry_id, rank=rank
        )
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status(f"Rank {rank} set.")
        self._refresh_matrix()

        # Restore cursor position after refresh
        table = self.query_one("#matrix", DataTable)
        table.move_cursor(row=cursor_row, column=cursor_col)

    def _handle_add_judge(self, judge_id: UUID | None) -> None:
        if judge_id is None:
            self._set_status("Add judge cancelled.")
            return

        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        if judge_id in competition.judge_ids:
            self._set_status("Judge already in competition.")
            return

        competition.judge_ids.append(judge_id)
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            participant = event_service.find_participant(event, judge_id)
            if participant:
                self._set_status(f"Judge {participant.number} added.")
            else:
                self._set_status("Judge added.")

        self._columns_built = False
        self._refresh_matrix()
        self._refresh_empty_overlay()

    def _handle_add_entry(self, entry_id: UUID | None) -> None:
        if entry_id is None:
            self._set_status("Add entry cancelled.")
            return

        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        if entry_id in competition.entry_ids:
            self._set_status("Entry already in competition.")
            return

        competition.entry_ids.append(entry_id)
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Entry added.")

        self._refresh_matrix()
        self._refresh_empty_overlay()

    def _handle_rename(self, name: str | None) -> None:
        if name is None:
            self._set_status("Rename cancelled.")
            return

        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        competition.name = name
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Competition renamed.")
        self._refresh_headers()

    def _handle_rank_input(
        self, judge_id: UUID, entry_id: UUID, value: str | None
    ) -> None:
        if value is None:
            return

        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        if value.strip() == "":
            removed = event_service.clear_rank_mark(
                event, self._competition_id, judge_id=judge_id, entry_id=entry_id
            )
            if removed:
                warnings = self._commit_change()
                if warnings:
                    self._set_status("; ".join(warnings))
                else:
                    self._set_status("Rank cleared.")
            self._refresh_matrix()
            return

        try:
            rank = int(value)
        except ValueError:
            self._set_status("Rank must be an integer.")
            return

        entry_count = len(competition.entry_ids)
        if rank < 1 or rank > entry_count:
            self._set_status(f"Rank must be between 1 and {entry_count}.")
            return

        event_service.set_rank_mark(
            event, self._competition_id, judge_id=judge_id, entry_id=entry_id, rank=rank
        )
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Rank updated.")
        self._refresh_matrix()

    def _refresh_headers(self) -> None:
        event, competition = self._get_event_competition()
        if competition is None:
            self.query_one("#title", Static).update("Competition: None")
        else:
            self.query_one("#title", Static).update(f"Competition: {competition.name}")

        if event:
            self.query_one("#event-info", Static).update(f"Event: {event.name}")
        else:
            self.query_one("#event-info", Static).update("Event: None")

    def _ensure_judge_columns(self) -> None:
        if self._columns_built:
            return

        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        table = self.query_one("#matrix", DataTable)
        table.clear(columns=True)
        table.add_columns("Entry")

        participant_lookup = {p.id: p for p in event.participants}
        for judge_id in competition.judge_ids:
            participant = participant_lookup.get(judge_id)
            label = participant.first_name if participant else str(judge_id)
            table.add_column(label)

        self._columns_built = True

    def _refresh_matrix(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        # Ensure columns are built first if needed
        if not self._columns_built:
            self._ensure_judge_columns()

        table = self.query_one("#matrix", DataTable)
        table.clear()
        self._visible_entry_ids = []
        self._visible_judge_ids = list(competition.judge_ids)

        participant_lookup = {p.id: p for p in event.participants}
        entry_lookup = {e.id: e for e in event.entries}

        for entry_id in competition.entry_ids:
            entry = entry_lookup.get(entry_id)
            if entry is None:
                continue
            self._visible_entry_ids.append(entry_id)
            label = event_service.entry_display_label(entry, participant_lookup)

            row_values: list[str | Text] = [label]
            for judge_id in self._visible_judge_ids:
                mark = _find_mark(competition, judge_id=judge_id, entry_id=entry_id)
                if mark:
                    row_values.append(Text(str(mark.rank), justify="center"))
                else:
                    row_values.append("")
            table.add_row(*row_values)

    def _refresh_results(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self.query_one("#results-content", Static).update("")
            return

        if competition.results is None or not competition.results.placements:
            self.query_one("#results-content", Static).update("Not computed.")
            return

        participant_lookup = {p.id: p for p in event.participants}
        entry_lookup = {e.id: e for e in event.entries}

        placements = list(competition.results.placements)
        labeled: list[tuple[int, str, float]] = []
        for placement in placements:
            entry = entry_lookup.get(placement.entry_id)
            if entry is None:
                continue
            label = event_service.entry_display_label(entry, participant_lookup)
            labeled.append((placement.rank, label, placement.average_rank))

        labeled.sort(key=lambda item: (item[0], item[1]))
        lines = []
        for rank, label, avg in labeled:
            lines.append(f"{rank}. {label}\n   (avg {avg:.2f})")

        self.query_one("#results-content", Static).update("\n".join(lines))

    def _refresh_empty_overlay(self) -> None:
        event, competition = self._get_event_competition()
        if competition is None:
            self.query_one("#empty-overlay", Static).update("")
            return

        if not competition.judge_ids and not competition.entry_ids:
            self.query_one("#empty-overlay", Static).update(
                "Press 'j' to add judges\nPress 'e' to add entries"
            )
        else:
            self.query_one("#empty-overlay", Static).update("")

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _commit_change(self) -> list[str]:
        committer = getattr(self.app, "commit_change", None)
        if committer is None:
            marker = getattr(self.app, "mark_dirty", None)
            if marker is not None:
                marker()
            return []
        return committer()

    def _get_event_competition(self) -> tuple[Event | None, Competition | None]:
        event = getattr(self.app, "event", None)
        if event is None:
            return None, None
        competition = event_service.find_competition(event, self._competition_id)
        return event, competition


def _find_mark(competition: Competition, *, judge_id: UUID, entry_id: UUID):
    for mark in competition.rank_marks:
        if mark.judge_id == judge_id and mark.entry_id == entry_id:
            return mark
    return None


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


def _entry_score(
    query: str, entry: Entry, participant_lookup: dict[UUID, Participant]
) -> int | None:
    if not query:
        return 0

    label = event_service.entry_display_label(entry, participant_lookup)
    member_numbers = " ".join(
        str(participant_lookup[m.participant_id].number)
        for m in entry.members
        if m.participant_id in participant_lookup
    )
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
