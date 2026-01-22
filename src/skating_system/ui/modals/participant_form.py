from __future__ import annotations

from textual.screen import ModalScreen
from textual.widgets import Static


class ParticipantForm(ModalScreen[None]):
    def compose(self):
        yield Static("Participant form (prototype)")
