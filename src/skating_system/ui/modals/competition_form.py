from __future__ import annotations

from dataclasses import dataclass

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static


@dataclass(frozen=True)
class CompetitionFormData:
    name: str


class CompetitionForm(ModalScreen[CompetitionFormData | None]):
    """Create a new competition (name only).

    Judges and entries are added later via edit.
    """

    DEFAULT_CSS = """
    CompetitionForm {
        align: center middle;
    }

    CompetitionForm > #dialog {
        width: 70%;
        max-width: 60;
        min-width: 40;
        height: auto;
        padding: 1 2;
        border: round $primary;
        background: $panel;
    }

    CompetitionForm .row {
        height: auto;
        margin-bottom: 1;
    }

    CompetitionForm #error {
        color: $error;
        height: auto;
        margin-bottom: 1;
    }

    CompetitionForm .buttons {
        align-horizontal: right;
        height: auto;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(
        self,
        *,
        title: str,
        name: str = "",
        confirm_label: str = "Create",
    ) -> None:
        super().__init__()
        self._title = title
        self._name = name
        self._confirm_label = confirm_label

    def compose(self):
        with Vertical(id="dialog"):
            yield Static(self._title, id="title")
            yield Static("", id="error")

            with Vertical(classes="row"):
                yield Static("Competition name")
                yield Input(self._name, id="name")

            with Horizontal(classes="buttons"):
                yield Button(self._confirm_label, id="confirm")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#name", Input).focus()

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
        name = self.query_one("#name", Input).value.strip()
        if not name:
            self.query_one("#error", Static).update("Competition name is required.")
            return
        self.dismiss(CompetitionFormData(name=name))
