from __future__ import annotations

from textual.screen import ModalScreen
from textual.widgets import Static


class CompetitionForm(ModalScreen[None]):
    def compose(self):
        yield Static("Competition form (prototype)")
