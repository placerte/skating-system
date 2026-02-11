from __future__ import annotations

from typing import cast
from uuid import UUID

from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from skating_system.domain.models import Competition, Event
from skating_system.services import event_service
from skating_system.services.ranking_service import compute_results
from skating_system.ui.app_state import AppState
from skating_system.ui.modals.text_prompt import TextPrompt


class RankingScreen(Screen[None]):
    BINDINGS = [
        ("enter", "edit", "Edit"),
        ("c", "clear", "Clear"),
        ("r", "recompute", "Recompute"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, competition_id: UUID) -> None:
        super().__init__()
        self._competition_id = competition_id
        self._columns_built = False

        self._visible_entry_ids: list[UUID] = []
        self._visible_judge_ids: list[UUID] = []

    def compose(self):
        yield Static("Ranking", id="title")
        yield Static("", id="event-info")
        yield Static("", id="competition-info")
        yield DataTable(id="matrix")
        yield Static("", id="results")
        yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#matrix", DataTable)
        table.add_columns("Entry")
        table.zebra_stripes = True

    def on_show(self) -> None:
        self._refresh_headers()
        self._ensure_columns()
        self._refresh_matrix()
        self._refresh_results()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_edit(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self._set_status("No competition loaded.")
            return

        table = self.query_one("#matrix", DataTable)
        row = table.cursor_row
        col = table.cursor_column
        if row is None or col is None:
            self._set_status("Select a cell.")
            return
        if col == 0:
            self._set_status("Select a judge column.")
            return

        if row < 0 or row >= len(self._visible_entry_ids):
            self._set_status("Invalid selection.")
            return
        if (col - 1) < 0 or (col - 1) >= len(self._visible_judge_ids):
            self._set_status("Invalid selection.")
            return

        entry_id = self._visible_entry_ids[row]
        judge_id = self._visible_judge_ids[col - 1]
        initial = ""
        existing = _find_mark(competition, judge_id=judge_id, entry_id=entry_id)
        if existing is not None:
            initial = str(existing.rank)

        prompt = TextPrompt(
            title="Set rank (empty clears)",
            placeholder="Rank",
            confirm_label="Set",
            initial_value=initial,
            allow_empty=True,
        )
        self.app.push_screen(
            prompt,
            lambda value: self._handle_rank_input(
                event,
                competition,
                judge_id=judge_id,
                entry_id=entry_id,
                value=value,
            ),
        )

    def action_clear(self) -> None:
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
            event,
            self._competition_id,
            judge_id=judge_id,
            entry_id=entry_id,
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

    def action_recompute(self) -> None:
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
            self._set_status("Results recomputed.")
        self._refresh_results()

    def _handle_rank_input(
        self,
        event: Event,
        competition: Competition,
        *,
        judge_id: UUID,
        entry_id: UUID,
        value: str | None,
    ) -> None:
        if value is None:
            return

        if value.strip() == "":
            removed = event_service.clear_rank_mark(
                event,
                self._competition_id,
                judge_id=judge_id,
                entry_id=entry_id,
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

        mark = event_service.set_rank_mark(
            event,
            self._competition_id,
            judge_id=judge_id,
            entry_id=entry_id,
            rank=rank,
        )
        if mark is None:
            self._set_status("Could not set rank.")
            return

        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Rank updated.")
        self._refresh_matrix()

    def _refresh_headers(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
        if event:
            self.query_one("#event-info", Static).update(f"Event: {event.name}")
        else:
            self.query_one("#event-info", Static).update("Event: None")

        _, competition = self._get_event_competition()
        if competition is None:
            self.query_one("#competition-info", Static).update("Competition: None")
        else:
            self.query_one("#competition-info", Static).update(
                f"Competition: {competition.name}"
            )

    def _ensure_columns(self) -> None:
        if self._columns_built:
            return

        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        table = self.query_one("#matrix", DataTable)
        participant_lookup = {p.id: p for p in event.participants}
        for judge_id in competition.judge_ids:
            participant = participant_lookup.get(judge_id)
            if participant is None:
                label = str(judge_id)
            else:
                label = str(participant.number)
            table.add_column(label)
        self._columns_built = True

    def _refresh_matrix(self) -> None:
        table = self.query_one("#matrix", DataTable)
        table.clear()
        self._visible_entry_ids = []
        self._visible_judge_ids = []

        event, competition = self._get_event_competition()
        if event is None or competition is None:
            return

        participant_lookup = {p.id: p for p in event.participants}
        entry_lookup = {e.id: e for e in event.entries}

        entry_ids = list(competition.entry_ids)
        judge_ids = list(competition.judge_ids)
        self._visible_judge_ids = judge_ids

        for entry_id in entry_ids:
            entry = entry_lookup.get(entry_id)
            if entry is None:
                continue
            self._visible_entry_ids.append(entry_id)
            label = event_service.entry_display_label(entry, participant_lookup)

            row_values: list[str] = [label]
            for judge_id in judge_ids:
                mark = _find_mark(competition, judge_id=judge_id, entry_id=entry_id)
                row_values.append(str(mark.rank) if mark is not None else "")
            table.add_row(*row_values)

    def _refresh_results(self) -> None:
        event, competition = self._get_event_competition()
        if event is None or competition is None:
            self.query_one("#results", Static).update("")
            return

        app = cast(AppState, self.app)
        results = app.get_competition_result(self._competition_id)
        if results is None or not results.placements:
            self.query_one("#results", Static).update("No results computed.")
            return

        participant_lookup = {p.id: p for p in event.participants}
        entry_lookup = {e.id: e for e in event.entries}

        placements = list(results.placements)
        labeled: list[tuple[float, str]] = []
        for placement in placements:
            entry = entry_lookup.get(placement.entry_id)
            if entry is None:
                continue
            label = event_service.entry_display_label(entry, participant_lookup)
            labeled.append((placement.final_place, label))

        labeled.sort(key=lambda item: (item[0], item[1]))
        lines = []
        for final_place, label in labeled:
            place_str = (
                f"{final_place:.1f}" if final_place % 1 != 0 else f"{int(final_place)}"
            )
            lines.append(f"{place_str}. {label}")
        self.query_one("#results", Static).update("Results\n" + "\n".join(lines))

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
