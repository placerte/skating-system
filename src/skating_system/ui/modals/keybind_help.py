from __future__ import annotations

from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class KeybindHelp(ModalScreen[None]):
    DEFAULT_CSS = """
    KeybindHelp {
        align: center middle;
    }

    KeybindHelp > #dialog {
        width: 70%;
        max-width: 80;
        min-width: 50;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        border: round $primary;
        background: $panel;
    }

    KeybindHelp #help-title {
        margin-bottom: 1;
        text-style: bold;
    }

    KeybindHelp #help-content {
        height: 1fr;
    }

    KeybindHelp #help-close {
        margin-top: 1;
        align-horizontal: right;
    }
    """

    BINDINGS = [("escape", "close", "Close"), ("?", "close", "Close")]

    def compose(self):
        with Vertical(id="dialog"):
            yield Static("Key bindings", id="help-title")
            with VerticalScroll(id="help-content"):
                yield Static(self._help_text())
            yield Button("Close", id="help-close")

    def on_button_pressed(self, _event: Button.Pressed) -> None:
        self.dismiss(None)

    def action_close(self) -> None:
        self.dismiss(None)

    def _help_text(self) -> str:
        return "\n".join(
            [
                "Navigation",
                "  h / j / k / l   Move left/down/up/right",
                "\nEditing",
                "  Enter           Edit selected judge cell",
                "  1-9             Quick rank",
                "  c               Clear rank",
                "  C               Compute results",
                "\nData",
                "  J               Add judge",
                "  E               Add entry",
                "  r               Rename",
                "  d               Remove",
                "\nDisplay",
                "  t               Toggle compact labels",
                "  p               Toggle side panel",
                "  [ / ]           Resize side panel",
                "\nOther",
                "  Esc             Back",
            ]
        )
