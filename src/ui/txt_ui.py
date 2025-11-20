from typing import Iterable
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Footer, Header, Static
from services.event_service import EventService
from ui.create_participant import CreateParticipantScreen
from textual import work


class ParticipantTUI(App):
    """
    Basic reader
    """

    CSS = """
    Screen {
        layout: vertical;
    }

    #event_title {
        padding: 1 2;
        background: $surface;
    }

    #table_container {
        height: 1fr;
        padding: 1 2;
    }
    
    DataTable {
        height: 100%;
        width: 100%;
    }
    """

    VIM_BINDINGS = [
        ("j", "cursor_down", ""),
        ("k", "cursor_up", ""),
        ("h", "cursor_left", ""),
        ("l", "cursor_right", "")
    ]

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reload", "Reload partipants"),
        ("a", "add_participant", "Add partipant"),
        *VIM_BINDINGS
    ]

    service: EventService

    def __init__(self, service: EventService, **kwargs):
        super().__init__(**kwargs)
        self.service = service

    def compose(self) -> ComposeResult:
        """Builds the UI layout"""
        yield Header(show_clock=True)

        # Event Title (read only for now)
        title: str = self.service.get_event().title
        yield Static(f"Event: {title}", id="event_title")

        # load the table container
        with Container(id="table_container"):
            yield DataTable(id="participants_table")

        yield Footer()

    @property
    def _table(self)->DataTable:
        table: DataTable = self.query_one("#participants_table", DataTable)
        return table


    async def on_mount(self):
        """configure and load the table"""
        #table: DataTable = self.query_one("#participants_table",DataTable)

        # Defining columns
        self._table.add_columns("Number", "First Name", "Last Name", "Email")

        # Details
        self._table.zebra_stripes = True
        self._table.cursor_type = "cell"

        # Initial load
        await self.action_reload()

    async def action_reload(self):
        """Reload participants_table"""
        table: DataTable = self.query_one("#participants_table",DataTable)

        table.clear()

        participants: Iterable = self.service.list_participants()

        for p in participants:
            table.add_row(str(p.number),
                          p.first_name,
                          p.last_name,
                          p.email)

    @work
    async def action_add_participant(self):
        result = await self.push_screen_wait(CreateParticipantScreen())

        print(result)

    def action_cursor_left(self):
        row, col = self._table.cursor_coordinate
        self._table.move_cursor(row=row, column=col -1, scroll=True)

    def action_cursor_right(self):
        row, col = self._table.cursor_coordinate
        self._table.move_cursor(row=row, column=col +1, scroll=True)

    def action_cursor_down(self):
        row, col = self._table.cursor_coordinate
        self._table.move_cursor(row=row+1, column=col, scroll=True)

    def action_cursor_up(self):
        row, col = self._table.cursor_coordinate
        self._table.move_cursor(row=row-1, column=col, scroll=True)
        
