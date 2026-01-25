from __future__ import annotations

from uuid import UUID

from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from skating_system.services import event_service
from skating_system.domain.models import Competition, Event
from skating_system.ui.modals.competition_form import (
    CompetitionForm,
    CompetitionFormData,
)
from skating_system.ui.modals.text_prompt import TextPrompt
from skating_system.ui.screens.competition_edit import CompetitionEditScreen


class CompetitionsScreen(Screen[None]):
    BINDINGS = [
        ("a", "add", "Add"),
        ("e", "edit", "Edit"),
        ("enter", "open", "Open"),
        ("/", "search", "Search"),
        ("escape", "back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._query = ""
        self._visible_competition_ids: list[UUID] = []

    def compose(self):
        yield Static("Competitions", id="title")
        yield Static("", id="event-info")
        yield Static("", id="filters")
        yield DataTable(id="competitions")
        yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#competitions", DataTable)
        table.add_columns("Name", "Judges", "Entries", "Ready", "Computed")
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

        form = CompetitionForm(title="Create competition", confirm_label="Create")
        self.app.push_screen(form, self._handle_add_result)

    def action_edit(self) -> None:
        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event loaded.")
            return

        competition_id = self._selected_competition_id()
        if competition_id is None:
            self._set_status("Select a competition to edit.")
            return

        competition = event_service.find_competition(event, competition_id)
        if competition is None:
            self._set_status("Selected competition no longer exists.")
            self._refresh_table()
            return

        self.app.push_screen(CompetitionEditScreen(competition_id))

    def action_open(self) -> None:
        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event loaded.")
            return

        competition_id = self._selected_competition_id()
        if competition_id is None:
            self._set_status("Select a competition to open.")
            return

        if event_service.find_competition(event, competition_id) is None:
            self._set_status("Selected competition no longer exists.")
            self._refresh_table()
            return

        self.app.push_screen(CompetitionEditScreen(competition_id))

    def action_search(self) -> None:
        prompt = TextPrompt(
            title="Search competitions",
            placeholder="Search…",
            confirm_label="Search",
            initial_value=self._query,
            allow_empty=True,
        )
        self.app.push_screen(prompt, self._handle_search_result)

    def _refresh_event_info(self) -> None:
        event = getattr(self.app, "event", None)
        if event:
            info = f"Event: {event.name}"
        else:
            info = "Event: None"
        self.query_one("#event-info", Static).update(info)

    def _refresh_table(self) -> None:
        table = self.query_one("#competitions", DataTable)
        table.clear()
        self._visible_competition_ids = []

        event = getattr(self.app, "event", None)
        if event is None:
            self.query_one("#filters", Static).update("")
            return

        competitions = _search_competitions(event, self._query)
        query_text = self._query or "(none)"
        self.query_one("#filters", Static).update(f"Search: {query_text}")

        for competition in competitions:
            self._visible_competition_ids.append(competition.id)
            ready = "yes" if _is_ready(competition) else ""
            computed = "yes" if competition.results is not None else ""
            table.add_row(
                competition.name,
                str(len(competition.judge_ids)),
                str(len(competition.entry_ids)),
                ready,
                computed,
            )

    def _selected_competition_id(self) -> UUID | None:
        table = self.query_one("#competitions", DataTable)
        row = table.cursor_row
        if row is None:
            return None
        if row < 0 or row >= len(self._visible_competition_ids):
            return None
        return self._visible_competition_ids[row]

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _handle_add_result(self, data: CompetitionFormData | None) -> None:
        if data is None:
            self._set_status("Add cancelled.")
            return

        event = getattr(self.app, "event", None)
        if event is None:
            self._set_status("No event loaded.")
            return

        event_service.add_competition(
            event,
            name=data.name,
            judge_ids=[],
            entry_ids=[],
        )
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Competition created. Use Edit to add judges/entries.")
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


def _search_competitions(event: Event, query: str) -> list[Competition]:
    query = query.strip()
    if not query:
        return list(event.competitions)

    scored: list[tuple[int, Competition]] = []
    for competition in event.competitions:
        score = event_service.fuzzy_match_score(query, competition.name)
        if score is not None:
            scored.append((score, competition))
    return [competition for _, competition in sorted(scored, key=lambda item: -item[0])]


def _is_ready(competition: Competition) -> bool:
    return len(competition.judge_ids) >= 1 and len(competition.entry_ids) >= 2
