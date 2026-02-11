from __future__ import annotations

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static


class TextPrompt(ModalScreen[str | None]):
    DEFAULT_CSS = """
    TextPrompt {
        align: center middle;
    }

    TextPrompt > #dialog {
        width: 60%;
        max-width: 60;
        min-width: 40;
        height: auto;
        padding: 1 2;
        border: round $primary;
        background: $panel;
    }

    TextPrompt #prompt-title {
        margin-bottom: 1;
        text-style: bold;
    }

    TextPrompt #prompt-input {
        margin-bottom: 1;
    }

    TextPrompt .buttons {
        align-horizontal: right;
        height: auto;
    }
    """
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(
        self,
        *,
        title: str,
        placeholder: str,
        confirm_label: str = "OK",
        initial_value: str = "",
        allow_empty: bool = False,
    ) -> None:
        super().__init__()
        self._title = title
        self._placeholder = placeholder
        self._confirm_label = confirm_label
        self._initial_value = initial_value
        self._allow_empty = allow_empty

    def compose(self):
        with Vertical(id="dialog"):
            yield Static(self._title, id="prompt-title")
            yield Input(
                self._initial_value,
                placeholder=self._placeholder,
                id="prompt-input",
            )
            with Horizontal(classes="buttons"):
                yield Button(self._confirm_label, id="confirm")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#prompt-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "confirm":
                self._confirm()
            case "cancel":
                self.dismiss(None)

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        self._confirm()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _confirm(self) -> None:
        value = self.query_one("#prompt-input", Input).value.strip()
        if not value and not self._allow_empty:
            self.dismiss(None)
            return
        self.dismiss(value)
