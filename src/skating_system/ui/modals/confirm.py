from __future__ import annotations

from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmPrompt(ModalScreen[bool]):
    DEFAULT_CSS = """
    ConfirmPrompt {
        align: center middle;
    }

    ConfirmPrompt > #dialog {
        width: 60%;
        max-width: 60;
        min-width: 40;
        height: auto;
        padding: 1 2;
        border: round $primary;
        background: $panel;
    }

    ConfirmPrompt #confirm-title {
        margin-bottom: 1;
        text-style: bold;
    }

    ConfirmPrompt #confirm-message {
        margin-bottom: 1;
    }

    ConfirmPrompt .buttons {
        align-horizontal: right;
        height: auto;
    }
    """

    BINDINGS = [
        Binding("y", "confirm", "", show=False),
        Binding("n", "cancel", "", show=False),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, *, title: str, message: str) -> None:
        super().__init__()
        self._title = title
        self._message = message

    def compose(self):
        with Vertical(id="dialog"):
            yield Static(self._title, id="confirm-title")
            yield Static(self._message, id="confirm-message")
            with Horizontal(classes="buttons"):
                yield Button("Yes", id="confirm")
                yield Button("No", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "confirm":
                self.dismiss(True)
            case "cancel":
                self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
