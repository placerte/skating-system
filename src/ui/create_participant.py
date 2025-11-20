from textual.message import Message
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label

class CreateParticipantScreen(ModalScreen):
    """ Modal screen to create a partipant"""

    CSS = """
    CreateParticipantScreen {
        align: center middle;
    }

    #dialog {
        height: auto;
        max-height: 23;
        overflow-y: auto;
        width: 60%;
        max-width: 80%;
        padding: 2 2;
        border: heavy $accent;
        background: $surface;
    }

    #buttons {
        align-horizontal: right;
        padding-top: 1;
    }

    Input {
        width: 100%;
        margin-bottom: 1;
    }
    """

    def compose(self):
        yield Container(
        Vertical(
                Label("Add participant", id="title"),
                Input(placeholder="First Name", id="first_name"),
                Input(placeholder="Last Name", id="last_name"),
                Input(placeholder="Email", id="email"),
                Horizontal(
                    Button("Cancel",id="cancel"),
                    Button("Save",id="save"),
                    id="buttons"),
            ),
        id= "dialog"
        )

    def on_mount(self):
        self.query_one("#first_name", Input).focus()


    def on_button_pressed(self, event: Button.Pressed):
        
        if event.button.id == "cancel":
            self.dismiss(False)
        elif event.button.id == "save":
            self._save_and_close()

    def _save_and_close(self):
        first_name = self.query_one("#first_name",Input).value.strip()
        last_name = self.query_one("#last_name",Input).value.strip()
        email = self.query_one("#email",Input).value.strip()

        if first_name == "" or last_name == "":
            raise NotImplementedError("Implement empty name error")

        self.dismiss({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            })
