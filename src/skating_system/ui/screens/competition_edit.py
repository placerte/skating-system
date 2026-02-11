from __future__ import annotations

from typing import cast
from uuid import UUID

from rich.text import Text
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from skating_system.domain.models import Competition, Entry, Event, Participant
from skating_system.services import event_service
from skating_system.services.ranking_service import compute_results
from skating_system.services.skating_scorer import SolveResult, classify_cell
from skating_system.ui.helpers import judge_letters
from skating_system.ui.modals.text_prompt import TextPrompt
from skating_system.ui.app_state import AppState


class MatrixScreen(Screen[None]):
    """Matrix-first scoring screen."""

    DEFAULT_CSS = """
    MatrixScreen {
        layout: horizontal;
    }

    MatrixScreen #main {
        width: 1fr;
    }

    MatrixScreen #sidebar {
        width: 35;
        padding: 1;
        border-left: solid $primary;
    }

    MatrixScreen #empty-overlay {
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
        self._column_signature: tuple[int, int] | None = None
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
                yield Static("Results", id="results-title")
                yield Static("", id="results-content")
                yield Static("Transcript", id="transcript-title")
                yield Static("", id="transcript-content")
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
        self._restore_cursor(None, None)

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
        if row is None or col is None or col == 0:
            self._set_status("Select a judge cell.")
            return

        if col > len(self._visible_judge_ids):
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

        if col > len(self._visible_judge_ids):
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
        result, errors = compute_results(competition)
        if errors or result is None:
            self._set_status("; ".join(errors) if errors else "Unable to compute.")
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
            judge_index = col - 1
            if 0 <= judge_index < len(self._visible_judge_ids):
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

        if col > len(self._visible_judge_ids):
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
        if competition is None:
            self.query_one("#title", Static).update("Competition: None")
        else:
            self.query_one("#title", Static).update(f"Competition: {competition.name}")

        if event:
            self.query_one("#event-info", Static).update(f"Event: {event.name}")
        else:
            self.query_one("#event-info", Static).update("Event: None")

    def _ensure_judge_columns(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        judge_count = len(competition.judge_ids)
        entry_count = len(competition.entry_ids)
        signature = (judge_count, entry_count)
        if self._columns_built and self._column_signature == signature:
            return

        table = self.query_one("#matrix", DataTable)
        table.clear(columns=True)
        headers = ["Entry"]
        # reference [S-260210-1.10], [S-260210-1.14]
        headers.extend(judge_letters(judge_count))
        headers.extend(self._cutoff_headers(entry_count))
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
            label = event_service.entry_display_label(entry, participant_lookup)

            row_values: list[str | Text] = [label]
            for judge_id in self._visible_judge_ids:
                mark = _find_mark(competition, judge_id=judge_id, entry_id=entry_id)
                row_values.append(
                    Text(str(mark.rank), justify="center") if mark else ""
                )

            row_values.extend(
                self._derived_cells(entry_id, solve_result, len(competition.entry_ids))
            )

            place = placements.get(entry_id)
            row_values.append(self._format_place(place) if place is not None else "")
            table.add_row(*row_values)

        self._restore_cursor(cursor_row, cursor_col)

    def _refresh_results(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self.query_one("#results-content", Static).update("")
            self.query_one("#transcript-content", Static).update("")
            return

        solve_result = self._get_solve_result()
        is_stale = self._is_stale()
        title = "Results (stale)" if is_stale else "Results"
        self.query_one("#results-title", Static).update(title)

        if solve_result is None:
            self.query_one("#results-content", Static).update("Not computed.")
            self.query_one("#transcript-content", Static).update("")
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
        transcript = self._render_transcript(
            solve_result, entry_lookup, participant_lookup
        )
        self.query_one("#transcript-content", Static).update(transcript)

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
                cells.append(Text(text_value, style="dim"))
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

    def _render_transcript(
        self,
        result: SolveResult,
        entry_lookup: dict[UUID, Entry],
        participant_lookup: dict[UUID, Participant],
    ) -> str:
        # reference [S-260210-1.18]
        def label_for_entry(entry_id: UUID) -> str:
            entry = entry_lookup.get(entry_id)
            if entry is None:
                return str(entry_id)
            return event_service.entry_display_label(entry, participant_lookup)

        lines: list[str] = []

        def visit(node, depth: int) -> None:
            indent = "  " * depth
            subset = ", ".join(label_for_entry(eid) for eid in node.subset_entry_ids)
            line = f"{indent}{node.rule_applied}: {node.text}"
            if subset:
                line = f"{line} [{subset}]"
            lines.append(line)
            for child in node.children:
                visit(child, depth + 1)

        visit(result.transcript_root, 0)
        return "\n".join(lines)

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
                table.move_cursor(row=0, column=1)
            return
        table.move_cursor(row=row, column=col)

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

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
