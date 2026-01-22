from __future__ import annotations

from textual.screen import ModalScreen
from textual.widgets import Static


class EntryForm(ModalScreen[None]):
    def compose(self):
        yield Static("Entry form (prototype)")
