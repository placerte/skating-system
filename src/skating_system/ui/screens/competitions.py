from __future__ import annotations

from textual.screen import Screen
from textual.widgets import Static


class CompetitionsScreen(Screen[None]):
    def compose(self):
        yield Static("Competitions", id="title")
        yield Static("", id="event-info")

    def on_show(self) -> None:
        self._refresh_event_info()

    def _refresh_event_info(self) -> None:
        event = getattr(self.app, "event", None)
        if event:
            info = f"Event: {event.name}"
        else:
            info = "Event: None"
        self.query_one("#event-info", Static).update(info)
