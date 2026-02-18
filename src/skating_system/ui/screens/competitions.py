from __future__ import annotations

from pathlib import Path
from typing import cast
from uuid import UUID

from textual import events
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from skating_system.services import event_service
from skating_system.domain.models import Competition, Event
from skating_system.ui.modals.competition_form import (
    CompetitionForm,
    CompetitionFormData,
)
from skating_system.ui.modals.confirm import ConfirmPrompt
from skating_system.ui.modals.text_prompt import TextPrompt
from skating_system.ui.app_state import AppState
from skating_system.ui.screens.competition_edit import MatrixScreen
from skating_system.ui.figlet_helpers import render_figlet
from skating_system.ui.datatable_export import (
    build_export_path,
    datatable_to_tsv_text,
    default_export_dir,
    export_datatable_to_csv,
)


class CompetitionsScreen(Screen[None]):
    BINDINGS = [
        Binding("a", "add", "Add"),
        Binding("e", "edit", "Edit"),
        Binding("enter", "edit", "", show=False),
        Binding("d", "duplicate", "Duplicate"),
        Binding("x", "delete_competition", "Delete"),
        Binding("E", "export_csv", "Export CSV"),
        Binding("y", "yank", "", show=False),
        Binding("/", "search", "Search"),
        Binding("l", "load_event", "Load"),
        Binding("s", "save_event", "Save"),
        Binding("r", "rename_event", "Rename"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._query = ""
        self._visible_competition_ids: list[UUID] = []

    def compose(self):
        yield Static("", id="event-title")
        yield Static("", id="screen-subtitle")
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

    def on_resume(self) -> None:
        self._refresh_event_info()
        self._refresh_table()

    def on_key(self, event: events.Key) -> None:
        if event.key not in {"h", "j", "k", "l"}:
            return
        focused = self.app.focused
        if not isinstance(focused, DataTable):
            return
        if event.key == "h":
            self.action_move_left()
        elif event.key == "j":
            self.action_move_down()
        elif event.key == "k":
            self.action_move_up()
        elif event.key == "l":
            self.action_move_right()
        event.prevent_default()
        event.stop()

    def action_back(self) -> None:
        self.app.exit()

    def action_add(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        form = CompetitionForm(title="Create competition", confirm_label="Create")
        self.app.push_screen(form, self._handle_add_result)

    def action_edit(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
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

        self.app.push_screen(MatrixScreen(competition_id))

    def action_open(self) -> None:
        # reference [S-260210-1.12]
        self.action_edit()

    def action_duplicate(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        competition_id = self._selected_competition_id()
        if competition_id is None:
            self._set_status("Select a competition to duplicate.")
            return

        new_competition = event_service.duplicate_competition(event, competition_id)
        if new_competition is None:
            self._set_status("Selected competition no longer exists.")
            self._refresh_table()
            return

        if app.competition_is_stale(competition_id):
            app.mark_competition_stale(new_competition.id)
        result = app.get_competition_result(competition_id)
        if result is not None:
            app.set_competition_result(new_competition.id, result)

        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Competition duplicated.")
        self._refresh_table()

    def action_export_csv(self) -> None:
        table = self.query_one("#competitions", DataTable)
        app = cast(AppState, self.app)
        event_name = app.event.name if app.event else "event"
        output_path = build_export_path(
            default_export_dir(),
            event_name=event_name,
            competition_name="competitions",
        )
        try:
            export_datatable_to_csv(table, output_path)
        except OSError as exc:
            self._set_status(f"Export failed: {exc}")
            return
        self._set_status(f"Exported table to {output_path}")

    def action_yank(self) -> None:
        table = self.query_one("#competitions", DataTable)
        text = datatable_to_tsv_text(table)
        self.app.copy_to_clipboard(text)
        self._set_status("Table copied to clipboard")

    def action_load_event(self) -> None:
        app = cast(AppState, self.app)
        default_dir = app.default_dir
        initial = app.file_path
        initial_value = str(initial) if initial else str(default_dir / "event.json")
        prompt = TextPrompt(
            title="Load event",
            placeholder="Event file path",
            confirm_label="Load",
            initial_value=initial_value,
        )
        self.app.push_screen(prompt, self._handle_load_prompt)

    def action_save_event(self) -> None:
        app = cast(AppState, self.app)
        default_dir = app.default_dir
        initial = app.file_path
        initial_value = str(initial) if initial else str(default_dir / "event.json")
        prompt = TextPrompt(
            title="Save event",
            placeholder="Event file path",
            confirm_label="Save",
            initial_value=initial_value,
        )
        self.app.push_screen(prompt, self._handle_save_prompt)

    def action_rename_event(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
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

    def action_search(self) -> None:
        prompt = TextPrompt(
            title="Search competitions",
            placeholder="Search…",
            confirm_label="Search",
            initial_value=self._query,
            allow_empty=True,
        )
        self.app.push_screen(prompt, self._handle_search_result)

    def action_delete_competition(self) -> None:
        competition_id = self._selected_competition_id()
        if competition_id is None:
            self._set_status("Select a competition to delete.")
            return

        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        competition = event_service.find_competition(event, competition_id)
        if competition is None:
            self._set_status("Selected competition no longer exists.")
            self._refresh_table()
            return

        prompt = ConfirmPrompt(
            title="Delete competition",
            message=f"Delete '{competition.name}'?",
        )
        self.app.push_screen(
            prompt,
            lambda confirmed: self._handle_delete_confirm(competition_id, confirmed),
        )

    def action_move_left(self) -> None:
        self._move_cursor(delta_row=0, delta_col=-1)

    def action_move_right(self) -> None:
        self._move_cursor(delta_row=0, delta_col=1)

    def action_move_up(self) -> None:
        self._move_cursor(delta_row=-1, delta_col=0)

    def action_move_down(self) -> None:
        self._move_cursor(delta_row=1, delta_col=0)

    def _refresh_event_info(self) -> None:
        app = cast(AppState, self.app)
        event = app.event
        event_name = event.name if event else "No event"
        event_widget = self.query_one("#event-title", Static)
        event_width = event_widget.size.width or self.size.width or 80
        title = render_figlet(
            event_name, font="smslant", width=event_width, align="center"
        )
        subtitle_widget = self.query_one("#screen-subtitle", Static)
        subtitle_width = subtitle_widget.size.width or event_width
        subtitle = render_figlet(
            "Competitions", font="mini", width=subtitle_width, align="left"
        )
        event_widget.update(title)
        subtitle_widget.update(subtitle)

    def _refresh_table(self) -> None:
        table = self.query_one("#competitions", DataTable)
        table.clear()
        self._visible_competition_ids = []

        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self.query_one("#filters", Static).update("")
            return

        competitions = _search_competitions(event, self._query)
        query_text = self._query or "(none)"
        self.query_one("#filters", Static).update(f"Search: {query_text}")

        for competition in competitions:
            self._visible_competition_ids.append(competition.id)
            ready = "yes" if _is_ready(competition) else ""
            result = app.get_competition_result(competition.id)
            stale = app.competition_is_stale(competition.id)
            if result is None:
                computed = ""
            elif stale:
                computed = "stale"
            else:
                computed = "yes"
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

        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        event_service.add_competition(
            event,
            name=data.name,
            judge_ids=[],
            entry_ids=[],
        )
        if event.competitions:
            app.mark_competition_stale(event.competitions[-1].id)
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
        app = cast(AppState, self.app)
        warnings = app.load_event(path)
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Event loaded.")
        self._refresh_event_info()
        self._refresh_table()

    def _handle_save_prompt(self, value: str | None) -> None:
        if value is None:
            self._set_status("Save cancelled.")
            return
        path = self._resolve_path(value)
        if path is None:
            self._set_status("Enter a file path to save.")
            return
        app = cast(AppState, self.app)
        warnings = app.save_event(path)
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Event saved.")
        self._refresh_event_info()

    def _handle_rename_prompt(self, name: str | None) -> None:
        if name is None:
            self._set_status("Rename cancelled.")
            return
        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event to rename.")
            return
        event.name = name
        warnings = app.commit_change()
        file_path = app.file_path
        if file_path is None:
            self._set_status("Event name updated (not saved yet).")
        elif warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Event name updated (auto-saved).")
        self._refresh_event_info()

    def _resolve_path(self, raw: str) -> Path | None:
        if not raw:
            return None
        path = Path(raw)
        if not path.is_absolute():
            app = cast(AppState, self.app)
            path = app.default_dir / path
        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")
        return path

    def _commit_change(self) -> list[str]:
        app = cast(AppState, self.app)
        app.mark_dirty()
        return app.commit_change()

    def _handle_delete_confirm(
        self, competition_id: UUID, confirmed: bool | None
    ) -> None:
        if not confirmed:
            self._set_status("Delete cancelled.")
            return

        app = cast(AppState, self.app)
        event = app.event
        if event is None:
            self._set_status("No event loaded.")
            return

        competition = event_service.find_competition(event, competition_id)
        if competition is None:
            self._set_status("Selected competition no longer exists.")
            self._refresh_table()
            return

        competition.is_obsolete = True
        warnings = self._commit_change()
        if warnings:
            self._set_status("; ".join(warnings))
        else:
            self._set_status("Competition deleted.")
        self._refresh_table()

    def _move_cursor(self, delta_row: int, delta_col: int) -> None:
        table = self.query_one("#competitions", DataTable)
        row = table.cursor_row
        col = table.cursor_column
        if row is None or col is None:
            return
        if table.row_count == 0 or len(table.columns) == 0:
            return
        target_row = max(0, min(table.row_count - 1, row + delta_row))
        target_col = max(0, min(len(table.columns) - 1, col + delta_col))
        table.move_cursor(row=target_row, column=target_col)


def _search_competitions(event: Event, query: str) -> list[Competition]:
    query = query.strip()
    visible = [
        competition for competition in event.competitions if not competition.is_obsolete
    ]
    if not query:
        return list(visible)

    scored: list[tuple[int, Competition]] = []
    for competition in visible:
        score = event_service.fuzzy_match_score(query, competition.name)
        if score is not None:
            scored.append((score, competition))
    return [competition for _, competition in sorted(scored, key=lambda item: -item[0])]


def _is_ready(competition: Competition) -> bool:
    return len(competition.judge_ids) >= 1 and len(competition.entry_ids) >= 2
