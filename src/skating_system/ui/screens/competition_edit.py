from __future__ import annotations

from typing import cast
from uuid import UUID

from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static, Tree

from skating_system.domain.models import Competition, Entry, Event, Participant
from skating_system.services import event_service
from skating_system.services.ranking_service import compute_results
from skating_system.services.skating_scorer import (
    SolveResult,
    classify_cell,
)
from skating_system.ui.helpers import judge_letters
from skating_system.ui.figlet_helpers import render_figlet
from skating_system.ui.modals.keybind_help import KeybindHelp
from skating_system.ui.modals.text_prompt import TextPrompt
from skating_system.ui.app_state import AppState
from skating_system.ui.datatable_export import (
    build_export_path,
    datatable_to_tsv_text,
    default_export_dir,
    export_datatable_to_csv,
)


class MatrixScreen(Screen[None]):
    """Matrix-first scoring screen."""

    DEFAULT_CSS = """
    MatrixScreen {
        layout: horizontal;
    }

    MatrixScreen.sidebar-collapsed #sidebar {
        display: none;
    }

    MatrixScreen #main {
        width: 1fr;
    }

    MatrixScreen #sidebar {
        width: 35;
        padding: 1;
        border-left: solid $primary;
    }

    MatrixScreen #transcript-scroll {
        height: 1fr;
    }

    MatrixScreen #empty-overlay {
        height: auto;
        color: $text-muted;
        text-align: center;
        margin-top: 4;
    }
    """

    BINDINGS = [
        Binding("J", "add_judge", "Add judge"),
        Binding("E", "add_entry", "Add entry"),
        Binding("r", "rename", "Rename"),
        Binding("enter", "edit_cell", "Edit rank"),
        Binding("c", "clear_cell", "Clear rank"),
        Binding("C", "compute", "Compute"),
        Binding("d", "remove", "Remove"),
        Binding("x", "export_csv", "Export CSV"),
        Binding("y", "yank", "", show=False),
        Binding("t", "toggle_labels", "Toggle labels"),
        Binding("?", "toggle_help", "Help"),
        Binding("escape", "back", "Back"),
        Binding("p", "toggle_panel", "Toggle panel", show=False),
        Binding("[", "sidebar_narrower", "", show=False),
        Binding("]", "sidebar_wider", "", show=False),
        Binding("h", "move_left", "", show=False),
        Binding("j", "move_down", "", show=False),
        Binding("k", "move_up", "", show=False),
        Binding("l", "move_right", "", show=False),
        Binding("1", "quick_rank(1)", "", show=False),
        Binding("2", "quick_rank(2)", "", show=False),
        Binding("3", "quick_rank(3)", "", show=False),
        Binding("4", "quick_rank(4)", "", show=False),
        Binding("5", "quick_rank(5)", "", show=False),
        Binding("6", "quick_rank(6)", "", show=False),
        Binding("7", "quick_rank(7)", "", show=False),
        Binding("8", "quick_rank(8)", "", show=False),
        Binding("9", "quick_rank(9)", "", show=False),
    ]

    def __init__(self, competition_id: UUID) -> None:
        super().__init__()
        self._competition_id = competition_id
        self._columns_built = False
        self._column_signature: tuple[int, int, bool] | None = None
        self._visible_entry_ids: list[UUID] = []
        self._visible_judge_ids: list[UUID] = []
        self._compact_labels = False
        self._sidebar_collapsed = True
        self._sidebar_width = 45

    def compose(self):
        with Horizontal():
            with Vertical(id="main"):
                yield Static("", id="event-title")
                yield Static("", id="competition-title")
                yield Static("", id="empty-overlay")
                yield DataTable(id="matrix")
                yield Static("", id="status")
                yield Footer()

            with Vertical(id="sidebar"):
                yield Static("Results", id="results-title")
                yield Static("", id="results-content")
                yield Static("Transcript", id="transcript-title")
                with VerticalScroll(id="transcript-scroll"):
                    yield Tree("Transcript", id="transcript-tree")
                yield Static("Press 'C' to compute", id="results-hint")

    def on_mount(self) -> None:
        table = self.query_one("#matrix", DataTable)
        table.add_columns("Entry")
        table.zebra_stripes = True
        self._apply_sidebar_width()
        self.set_class(self._sidebar_collapsed, "sidebar-collapsed")

    def on_show(self) -> None:
        self._refresh_headers()
        self._ensure_judge_columns()
        self._refresh_matrix()
        self._refresh_results()
        self._refresh_empty_overlay()
        self._restore_cursor(None, None)

    def on_resize(self) -> None:
        self._refresh_headers()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_add_judge(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return
        prompt = TextPrompt(
            title="Add judge",
            placeholder="Judge name",
            confirm_label="Add",
        )
        self.app.push_screen(prompt, self._handle_add_judge_name)

    def action_add_entry(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return
        prompt = TextPrompt(
            title="Add entry",
            placeholder="Entry name",
            confirm_label="Add",
        )
        self.app.push_screen(prompt, self._handle_add_entry_name)

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
        if row is None or col is None:
            self._set_status("Select a judge cell.")
            return

        judge_index = self._judge_index_for_column(col)
        if judge_index is None:
            self._set_status("Select a judge cell.")
            return

        if row < 0 or row >= len(self._visible_entry_ids):
            return

        entry_id = self._visible_entry_ids[row]
        judge_id = self._visible_judge_ids[judge_index]

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
        if row is None or col is None:
            self._set_status("Select a judge cell to clear.")
            return

        judge_index = self._judge_index_for_column(col)
        if judge_index is None:
            self._set_status("Select a judge cell to clear.")
            return

        if row < 0 or row >= len(self._visible_entry_ids):
            return
        entry_id = self._visible_entry_ids[row]
        judge_id = self._visible_judge_ids[judge_index]

        removed = event_service.clear_rank_mark(
            event, self._competition_id, judge_id=judge_id, entry_id=entry_id
        )
        if removed:
            self._mark_stale()
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
        entry_labels = self._entry_label_lookup(event)
        result, errors = compute_results(competition, entry_labels=entry_labels)
        if errors or result is None:
            friendly = self._friendly_validation_errors(event, competition)
            message = friendly or errors or ["Unable to compute."]
            self._set_status("; ".join(message))
            return

        app = cast(AppState, self.app)
        app.set_competition_result(self._competition_id, result)
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Results computed.")
        self._refresh_matrix()
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
                self._mark_stale()
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
            judge_index = self._judge_index_for_column(col)
            if judge_index is not None:
                judge_id = self._visible_judge_ids[judge_index]
                competition.judge_ids = [
                    jid for jid in competition.judge_ids if jid != judge_id
                ]
                competition.rank_marks = [
                    m for m in competition.rank_marks if m.judge_id != judge_id
                ]
                self._mark_stale()
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

    def action_toggle_labels(self) -> None:
        self._compact_labels = not self._compact_labels
        self._columns_built = False
        self._refresh_matrix()

    def action_toggle_panel(self) -> None:
        self._sidebar_collapsed = not self._sidebar_collapsed
        self.set_class(self._sidebar_collapsed, "sidebar-collapsed")
        self.call_after_refresh(self._refresh_headers)

    def action_sidebar_narrower(self) -> None:
        self._sidebar_width = max(25, self._sidebar_width - 5)
        self._apply_sidebar_width()
        self.call_after_refresh(self._refresh_headers)

    def action_sidebar_wider(self) -> None:
        self._sidebar_width = min(90, self._sidebar_width + 5)
        self._apply_sidebar_width()
        self.call_after_refresh(self._refresh_headers)

    def action_move_left(self) -> None:
        self._move_cursor(delta_row=0, delta_col=-1)

    def action_move_right(self) -> None:
        self._move_cursor(delta_row=0, delta_col=1)

    def action_move_up(self) -> None:
        self._move_cursor(delta_row=-1, delta_col=0)

    def action_move_down(self) -> None:
        self._move_cursor(delta_row=1, delta_col=0)

    def action_toggle_help(self) -> None:
        self.app.push_screen(KeybindHelp())

    def action_export_csv(self) -> None:
        table = self.query_one("#matrix", DataTable)
        event, competition = self._get_event_competition()
        event_name = event.name if event else "event"
        competition_name = competition.name if competition else "competition"
        output_path = build_export_path(
            default_export_dir(),
            event_name=event_name,
            competition_name=competition_name,
        )
        try:
            export_datatable_to_csv(table, output_path)
        except OSError as exc:
            self._set_status(f"Export failed: {exc}")
            return
        self._set_status(f"Exported table to {output_path}")

    def action_yank(self) -> None:
        table = self.query_one("#matrix", DataTable)
        text = datatable_to_tsv_text(table)
        self.app.copy_to_clipboard(text)
        self._set_status("Table copied to clipboard")

    def action_quick_rank(self, rank: int) -> None:
        """Quick rank entry: press 1-9 to set rank on selected cell."""
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        table = self.query_one("#matrix", DataTable)
        row = table.cursor_row
        col = table.cursor_column
        if row is None or col is None:
            return

        judge_index = self._judge_index_for_column(col)
        if judge_index is None:
            return

        if row < 0 or row >= len(self._visible_entry_ids):
            return
        entry_id = self._visible_entry_ids[row]
        judge_id = self._visible_judge_ids[judge_index]

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
        self._mark_stale()
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status(f"Rank {rank} set.")
        self._refresh_matrix()

        # Restore cursor position after refresh
        table = self.query_one("#matrix", DataTable)
        table.move_cursor(row=cursor_row, column=cursor_col)

    def _handle_add_judge_name(self, name: str | None) -> None:
        if name is None:
            self._set_status("Add judge cancelled.")
            return
        name = name.strip()
        if not name:
            self._set_status("Judge name is required.")
            return

        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        # reference [S-260210-1.8], [S-260210-1.9]
        existing = next(
            (
                participant
                for participant in event.participants
                if participant.first_name == name and participant.last_name == ""
            ),
            None,
        )
        participant = existing or event_service.add_participant(
            event, first_name=name, last_name=""
        )
        if participant.id in competition.judge_ids:
            self._set_status("Judge already in competition.")
            return

        competition.judge_ids.append(participant.id)
        self._mark_stale()
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Judge added.")

        self._columns_built = False
        self._refresh_matrix()
        self._refresh_empty_overlay()

    def _handle_add_entry_name(self, name: str | None) -> None:
        if name is None:
            self._set_status("Add entry cancelled.")
            return
        name = name.strip()
        if not name:
            self._set_status("Entry name is required.")
            return

        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        # reference [S-260210-1.8], [S-260210-1.9]
        existing = next((entry for entry in event.entries if entry.name == name), None)
        entry = existing or event_service.add_entry(event, name=name, members=[])
        if entry.id in competition.entry_ids:
            self._set_status("Entry already in competition.")
            return

        competition.entry_ids.append(entry.id)
        self._mark_stale()
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
                self._mark_stale()
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
        self._mark_stale()
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Rank updated.")
        self._refresh_matrix()

    def _refresh_headers(self) -> None:
        event, competition = self._get_event_competition()
        event_widget = self.query_one("#event-title", Static)
        event_width = event_widget.size.width or self.size.width or 80
        event_name = event.name if event else "No event"
        event_title = render_figlet(
            event_name, font="smslant", width=event_width, align="center"
        )
        competition_widget = self.query_one("#competition-title", Static)
        competition_width = competition_widget.size.width or event_width
        competition_name = competition.name if competition else "No competition"
        competition_title = render_figlet(
            competition_name, font="mini", width=competition_width, align="left"
        )
        event_widget.update(event_title)
        competition_widget.update(competition_title)

    def _ensure_judge_columns(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        judge_count = len(competition.judge_ids)
        entry_count = len(competition.entry_ids)
        signature = (judge_count, entry_count, self._compact_labels)
        if self._columns_built and self._column_signature == signature:
            return

        table = self.query_one("#matrix", DataTable)
        table.clear(columns=True)
        headers = ["Entry", " "]
        headers.extend(self._judge_header_labels(event, competition))
        headers.append(" ")
        headers.extend(self._cutoff_headers(entry_count))
        headers.append(" ")
        headers.append("Place")
        table.add_columns(*headers)

        self._visible_judge_ids = list(competition.judge_ids)
        self._columns_built = True
        self._column_signature = signature

    def _refresh_matrix(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        table = self.query_one("#matrix", DataTable)
        cursor_row = table.cursor_row
        cursor_col = table.cursor_column

        self._ensure_judge_columns()
        table.clear()
        self._visible_entry_ids = []
        self._visible_judge_ids = list(competition.judge_ids)

        participant_lookup = {p.id: p for p in event.participants}
        entry_lookup = {e.id: e for e in event.entries}
        solve_result = self._get_solve_result()
        if self._is_stale():
            solve_result = None

        placements = {}
        if solve_result is not None:
            placements = {
                placement.entry_id: placement.final_place
                for placement in solve_result.placements
            }

        for entry_id in competition.entry_ids:
            entry = entry_lookup.get(entry_id)
            if entry is None:
                continue
            self._visible_entry_ids.append(entry_id)
            label = self._entry_label(entry, participant_lookup)

            row_values: list[str | Text] = [label, ""]
            for judge_id in self._visible_judge_ids:
                mark = _find_mark(competition, judge_id=judge_id, entry_id=entry_id)
                row_values.append(
                    Text(str(mark.rank), justify="center") if mark else ""
                )

            row_values.append("")
            row_values.extend(
                self._derived_cells(entry_id, solve_result, len(competition.entry_ids))
            )

            place = placements.get(entry_id)
            row_values.append("")
            row_values.append(self._format_place(place) if place is not None else "")
            table.add_row(*row_values)

        self._restore_cursor(cursor_row, cursor_col)

    def _refresh_results(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self.query_one("#results-content", Static).update("")
            self._clear_transcript_tree()
            return

        solve_result = self._get_solve_result()
        is_stale = self._is_stale()
        title = "Results (stale)" if is_stale else "Results"
        self.query_one("#results-title", Static).update(title)

        if solve_result is None:
            self.query_one("#results-content", Static).update("Not computed.")
            self._clear_transcript_tree()
            return

        participant_lookup = {p.id: p for p in event.participants}
        entry_lookup = {e.id: e for e in event.entries}
        labeled: list[tuple[float, str]] = []
        for placement in solve_result.placements:
            entry = entry_lookup.get(placement.entry_id)
            if entry is None:
                continue
            label = event_service.entry_display_label(entry, participant_lookup)
            labeled.append((placement.final_place, label))

        labeled.sort(key=lambda item: (item[0], item[1]))
        lines = []
        for final_place, label in labeled:
            place_str = self._format_place(final_place)
            lines.append(f"{place_str}. {label}")

        self.query_one("#results-content", Static).update("\n".join(lines))
        self._render_transcript_tree(solve_result)

    def _refresh_empty_overlay(self) -> None:
        event, competition = self._get_event_competition()
        if competition is None:
            overlay = self.query_one("#empty-overlay", Static)
            overlay.display = False
            overlay.update("")
            return

        if not competition.judge_ids and not competition.entry_ids:
            overlay = self.query_one("#empty-overlay", Static)
            overlay.display = True
            overlay.update("Press 'J' to add judges\nPress 'E' to add entries")
        else:
            overlay = self.query_one("#empty-overlay", Static)
            overlay.display = False
            overlay.update("")

    def _mark_stale(self) -> None:
        # reference [S-260210-1.19]
        app = cast(AppState, self.app)
        app.mark_competition_stale(self._competition_id)

    def _is_stale(self) -> bool:
        app = cast(AppState, self.app)
        return app.competition_is_stale(self._competition_id)

    def _get_solve_result(self) -> SolveResult | None:
        app = cast(AppState, self.app)
        return app.get_competition_result(self._competition_id)

    def _cutoff_headers(self, entry_count: int) -> list[str]:
        headers: list[str] = []
        for index in range(1, entry_count + 1):
            headers.append("1" if index == 1 else f"1-{index}")
        return headers

    def _derived_cells(
        self, entry_id: UUID, result: SolveResult | None, entry_count: int
    ) -> list[str | Text]:
        # reference [S-260210-1.2], [S-260210-1.3], [S-260210-1.13], [S-260210-1.15],
        # reference [S-260210-1.16]
        if result is None:
            return [""] * entry_count

        derived = result.derived_table
        counts = derived.counts_by_entry.get(entry_id)
        sums = derived.sums_by_entry.get(entry_id)
        majors = derived.majorities_by_entry.get(entry_id)
        cutoff = derived.cutoff_by_entry.get(entry_id, entry_count)
        if counts is None or sums is None or majors is None:
            return [""] * entry_count
        if (
            len(counts) < entry_count
            or len(sums) < entry_count
            or len(majors) < entry_count
        ):
            return [""] * entry_count

        cells: list[str | Text] = []
        for index in range(entry_count):
            column_index = index + 1
            count = counts[index]
            sum_ = sums[index]
            has_majority = majors[index]
            text_value = f"{count}{'*' if has_majority else ''} ({sum_})"
            classification = classify_cell(
                count=count,
                sum_=sum_,
                column_index=column_index,
                cutoff=cutoff,
            )
            if classification.is_dead:
                cells.append(Text(text_value, style="dim #4a4a4a"))
                continue

            primary = f"{count}{'*' if has_majority else ''}"
            text = Text(primary)
            if classification.is_decisive:
                text.stylize("bold", 0, len(primary))
            text.append(f" ({sum_})", style="dim")
            cells.append(text)

        return cells

    def _format_place(self, place: float) -> str:
        if place % 1 != 0:
            return f"{place:.1f}"
        return f"{int(place)}"

    def _friendly_validation_errors(
        self, event: Event, competition: Competition
    ) -> list[str]:
        entry_ids = list(competition.entry_ids)
        judge_ids = list(competition.judge_ids)
        entry_count = len(entry_ids)

        participant_lookup = {p.id: p for p in event.participants}
        entry_lookup = {e.id: e for e in event.entries}

        def judge_label(judge_id: UUID) -> str:
            participant = participant_lookup.get(judge_id)
            if participant is None:
                return "Unknown judge"
            name = f"{participant.first_name} {participant.last_name}".strip()
            return name or "Unknown judge"

        def entry_label(entry_id: UUID) -> str:
            entry = entry_lookup.get(entry_id)
            if entry is None:
                return "Unknown entry"
            return event_service.entry_display_label(entry, participant_lookup)

        errors: list[str] = []
        entry_set = set(entry_ids)
        judge_set = set(judge_ids)

        for mark in competition.rank_marks:
            if mark.judge_id not in judge_set:
                errors.append("Unknown judge in rank marks.")
            if mark.entry_id not in entry_set:
                errors.append("Unknown entry in rank marks.")
            if mark.rank < 1 or mark.rank > entry_count:
                errors.append(
                    f"Rank {mark.rank} out of range for entry {entry_label(mark.entry_id)}."
                )

        for judge_id in judge_ids:
            seen_entries: set[UUID] = set()
            ranks: list[int] = []
            for mark in competition.rank_marks:
                if mark.judge_id != judge_id:
                    continue
                if mark.entry_id in seen_entries:
                    errors.append(
                        "Duplicate rank mark for judge "
                        f"{judge_label(judge_id)} and entry {entry_label(mark.entry_id)}."
                    )
                    continue
                if mark.entry_id not in entry_set:
                    continue
                seen_entries.add(mark.entry_id)
                ranks.append(mark.rank)

            missing = [
                entry_id for entry_id in entry_ids if entry_id not in seen_entries
            ]
            if missing:
                labels = ", ".join(entry_label(entry_id) for entry_id in missing)
                errors.append(
                    "Judge "
                    f"{judge_label(judge_id)} missing ranks for {len(missing)} entries: "
                    f"{labels}."
                )

            if len(ranks) != len(set(ranks)):
                errors.append(f"Judge {judge_label(judge_id)} has duplicate ranks.")

        if not entry_ids or not judge_ids:
            errors.append("Competition requires at least one judge and one entry.")

        return errors

    def _clear_transcript_tree(self) -> None:
        tree = self.query_one("#transcript-tree", Tree)
        tree.clear()

    def _render_transcript_tree(self, result: SolveResult) -> None:
        tree = self.query_one("#transcript-tree", Tree)
        tree.clear()
        tree.show_root = False

        def render_label(text: str) -> Text:
            if text.startswith("**") and text.endswith("**"):
                return Text(text.strip("*"), style="bold")
            return Text(text)

        def build(node, parent) -> None:
            if node.text is None:
                parent.add_leaf(" ")
                return
            label = render_label(node.text)
            if node.children:
                child_node = parent.add(label, expand=True)
                for child in node.children:
                    build(child, child_node)
            else:
                parent.add_leaf(label)

        for child in result.transcript_root.children:
            build(child, tree.root)

    def _entry_label_lookup(self, event: Event) -> dict[UUID, str]:
        participant_lookup = {p.id: p for p in event.participants}
        return {
            entry.id: self._label_first_word(
                event_service.entry_display_label(entry, participant_lookup)
            )
            for entry in event.entries
        }

    def _restore_cursor(self, row: int | None, col: int | None) -> None:
        # reference [S-260210-1.11]
        table = self.query_one("#matrix", DataTable)
        row_count = table.row_count
        col_count = len(table.columns)
        if (
            row is None
            or col is None
            or row < 0
            or col < 0
            or row >= row_count
            or col >= col_count
        ):
            if row_count > 0 and col_count > 1:
                table.move_cursor(row=0, column=2)
            return
        table.move_cursor(row=row, column=col)

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _apply_sidebar_width(self) -> None:
        sidebar = self.query_one("#sidebar", Vertical)
        sidebar.styles.width = self._sidebar_width

    def _move_cursor(self, delta_row: int, delta_col: int) -> None:
        table = self.query_one("#matrix", DataTable)
        row = table.cursor_row
        col = table.cursor_column
        if row is None or col is None:
            return
        if table.row_count == 0 or len(table.columns) == 0:
            return
        target_row = max(0, min(table.row_count - 1, row + delta_row))
        target_col = max(0, min(len(table.columns) - 1, col + delta_col))
        table.move_cursor(row=target_row, column=target_col)

    def _judge_index_for_column(self, column: int) -> int | None:
        if column < 2:
            return None
        start = 2
        end = start + len(self._visible_judge_ids) - 1
        if column < start or column > end:
            return None
        return column - start

    def _label_first_word(self, label: str) -> str:
        cleaned = label.strip()
        return cleaned.split()[0] if cleaned else label

    def _entry_label(
        self,
        entry: Entry,
        participant_lookup: dict[UUID, Participant],
    ) -> str:
        label = event_service.entry_display_label(entry, participant_lookup)
        if self._compact_labels:
            return self._label_first_word(label)
        return label

    def _judge_header_labels(
        self,
        event: Event,
        competition: Competition,
    ) -> list[str]:
        participant_lookup = {p.id: p for p in event.participants}
        letters = judge_letters(len(competition.judge_ids))
        labels: list[str] = []
        for index, judge_id in enumerate(competition.judge_ids):
            letter = letters[index] if index < len(letters) else "?"
            participant = participant_lookup.get(judge_id)
            if participant is None:
                label = letter
            else:
                label = (
                    f"{letter} {participant.first_name} {participant.last_name}".strip()
                )
            if self._compact_labels:
                label = letter
            labels.append(label)
        return labels

    def _commit_change(self) -> list[str]:
        app = cast(AppState, self.app)
        app.mark_dirty()
        return app.commit_change()

    def _get_event_competition(self) -> tuple[Event | None, Competition | None]:
        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            return None, None
        competition = event_service.find_competition(event, self._competition_id)
        return event, competition


def _find_mark(competition: Competition, *, judge_id: UUID, entry_id: UUID):
    for mark in competition.rank_marks:
        if mark.judge_id == judge_id and mark.entry_id == entry_id:
            return mark
    return None
