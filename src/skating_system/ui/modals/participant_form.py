from __future__ import annotations

from dataclasses import dataclass

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static


@dataclass(frozen=True)
class ParticipantFormData:
    first_name: str
    last_name: str
    email: str | None


class ParticipantForm(ModalScreen[ParticipantFormData | None]):
    DEFAULT_CSS = """
    ParticipantForm {
        align: center middle;
    }

    ParticipantForm > #dialog {
        width: 70%;
        max-width: 72;
        min-width: 44;
        height: auto;
        padding: 1 2;
        border: round $primary;
        background: $panel;
    }

    ParticipantForm .row {
        height: auto;
        margin-bottom: 1;
    }

    ParticipantForm #error {
        color: $error;
        height: auto;
        margin-bottom: 1;
    }

    ParticipantForm .buttons {
        align-horizontal: right;
        height: auto;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        *,
        title: str,
        first_name: str = "",
        last_name: str = "",
        email: str | None = None,
        confirm_label: str = "Save",
    ) -> None:
        super().__init__()
        self._title = title
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._confirm_label = confirm_label

    def compose(self):
        with Vertical(id="dialog"):
            yield Static(self._title, id="title")
            yield Static("", id="error")

            with Vertical(classes="row"):
                yield Static("First name")
                yield Input(self._first_name, id="first_name")

            with Vertical(classes="row"):
                yield Static("Last name")
                yield Input(self._last_name, id="last_name")

            with Vertical(classes="row"):
                yield Static("Email (optional)")
                yield Input(self._email or "", id="email")

            with Horizontal(classes="buttons"):
                yield Button(self._confirm_label, id="confirm")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#first_name", Input).focus()

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
        first_name = self.query_one("#first_name", Input).value.strip()
        last_name = self.query_one("#last_name", Input).value.strip()
        email_raw = self.query_one("#email", Input).value.strip()
        email = email_raw if email_raw else None

        if not first_name or not last_name:
            self.query_one("#error", Static).update("First and last name are required.")
            return

        self.dismiss(
            ParticipantFormData(
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
        )
