from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar
from uuid import UUID

from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, OptionList, Static
from textual.widgets.option_list import Option

T = TypeVar("T")


@dataclass(frozen=True)
class RankedItem(Generic[T]):
    score: int
    item: T


class TypeaheadSelect(Widget, Generic[T]):
    """Typeahead / autocomplete combobox.

    This is a small widget that behaves like a common web "combobox":

    - type to filter
    - up/down to change highlighted suggestion
    - enter selects the current highlighted/best suggestion
    """

    DEFAULT_CSS = """
    TypeaheadSelect {
        height: auto;
    }

    TypeaheadSelect #label {
        height: auto;
        margin-bottom: 0;
    }

    TypeaheadSelect #query {
        margin-bottom: 1;
    }

    TypeaheadSelect #options {
        height: 8;
        border: round $surface;
    }
    """

    BINDINGS = [
        ("down", "cursor_down", "Next"),
        ("up", "cursor_up", "Prev"),
    ]

    class Selected(Message):
        def __init__(self, *, sender: "TypeaheadSelect", item: Any, item_id: UUID):
            super().__init__()
            self.set_sender(sender)
            self.widget_id = sender.id
            self.item = item
            self.item_id = item_id

    def __init__(
        self,
        *,
        label: str,
        placeholder: str,
        items: list[T],
        get_id: Callable[[T], UUID],
        get_label: Callable[[T], str],
        score: Callable[[str, T], int | None],
        max_options: int = 8,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._label = label
        self._placeholder = placeholder

        self._items = list(items)
        self._get_id = get_id
        self._get_label = get_label
        self._score = score
        self._max_options = max_options

        self._current_ranked: list[T] = []
        self._id_to_item: dict[UUID, T] = {}

    def compose(self):
        with Vertical():
            yield Static(self._label, id="label")
            yield Input(placeholder=self._placeholder, id="query")
            yield OptionList(id="options")

    def on_mount(self) -> None:
        self._refresh("")

    def focus_query(self) -> None:
        self.query_one("#query", Input).focus()

    def clear_query(self) -> None:
        self.query_one("#query", Input).value = ""
        self._refresh("")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "query":
            return
        self._refresh(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "query":
            return
        self._confirm_highlighted_or_best()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id != "options":
            return

        option_id = event.option.id
        if option_id is None:
            return
        try:
            item_id = UUID(str(option_id))
        except ValueError:
            return

        item = self._id_to_item.get(item_id)
        if item is None:
            return

        self.post_message(self.Selected(sender=self, item=item, item_id=item_id))

    def action_cursor_down(self) -> None:
        focused = getattr(self.screen, "focused", None)
        if focused != self.query_one("#query", Input):
            return
        self.query_one("#options", OptionList).action_cursor_down()

    def action_cursor_up(self) -> None:
        focused = getattr(self.screen, "focused", None)
        if focused != self.query_one("#query", Input):
            return
        self.query_one("#options", OptionList).action_cursor_up()

    def _confirm_highlighted_or_best(self) -> None:
        options = self.query_one("#options", OptionList)
        highlighted = options.highlighted_option
        if highlighted is not None and highlighted.id is not None:
            try:
                item_id = UUID(str(highlighted.id))
            except ValueError:
                item_id = None
            if item_id is not None:
                item = self._id_to_item.get(item_id)
                if item is not None:
                    self.post_message(
                        self.Selected(sender=self, item=item, item_id=item_id)
                    )
                    return

        if self._current_ranked:
            item = self._current_ranked[0]
            self.post_message(
                self.Selected(
                    sender=self,
                    item=item,
                    item_id=self._get_id(item),
                )
            )

    def _refresh(self, query: str) -> None:
        query = query.strip()
        ranked: list[RankedItem[T]] = []
        for item in self._items:
            s = self._score(query, item)
            if s is None:
                continue
            ranked.append(RankedItem(score=s, item=item))

        ranked.sort(key=lambda r: -r.score)
        self._current_ranked = [r.item for r in ranked[: self._max_options]]
        self._id_to_item = {self._get_id(item): item for item in self._current_ranked}

        options = self.query_one("#options", OptionList)
        options.clear_options()
        for item in self._current_ranked:
            item_id = self._get_id(item)
            options.add_option(Option(self._get_label(item), id=str(item_id)))

        if options.option_count:
            options.highlighted = 0
