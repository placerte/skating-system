from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar
from uuid import UUID

from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from skating_system.ui.widgets.typeahead_select import TypeaheadSelect

T = TypeVar("T")


class TypeaheadPicker(ModalScreen[UUID | None], Generic[T]):
    """Small modal wrapping TypeaheadSelect.

    Opens a picker, returns selected item ID or None.
    """

    DEFAULT_CSS = """
    TypeaheadPicker {
        align: center middle;
    }

    TypeaheadPicker > #dialog {
        width: 80%;
        max-width: 90;
        min-width: 50;
        height: auto;
        padding: 1 2;
        border: round $primary;
        background: $panel;
    }

    TypeaheadPicker #title {
        margin-bottom: 1;
        text-style: bold;
    }

    TypeaheadPicker #error {
        color: $error;
        height: auto;
        margin-bottom: 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(
        self,
        *,
        title: str,
        label: str,
        placeholder: str,
        items: list[T],
        get_id: Callable[[T], UUID],
        get_label: Callable[[T], str],
        score: Callable[[str, T], int | None],
    ) -> None:
        super().__init__()
        self._title = title
        self._label = label
        self._placeholder = placeholder
        self._items = items
        self._get_id = get_id
        self._get_label = get_label
        self._score = score

    def compose(self):
        with Vertical(id="dialog"):
            yield Static(self._title, id="title")
            yield Static("", id="error")
            yield TypeaheadSelect[T](
                label=self._label,
                placeholder=self._placeholder,
                items=self._items,
                get_id=self._get_id,
                get_label=self._get_label,
                score=self._score,
                id="picker",
            )

    def on_mount(self) -> None:
        self.query_one("#picker", TypeaheadSelect).focus_query()

    def on_typeahead_select_selected(self, event: Any) -> None:
        if event.widget_id != "picker":
            return
        self.dismiss(event.item_id)

    def action_cancel(self) -> None:
        self.dismiss(None)
