from __future__ import annotations

from typing import cast
from uuid import UUID

import pytest
from textual.app import App
from textual.widgets import DataTable

from skating_system.domain.models import EntryMember
from skating_system.services import event_service
from skating_system.ui.datatable_export import datatable_to_tsv_text
from skating_system.ui.screens.competition_edit import MatrixScreen
from skating_system.ui.screens.competitions import CompetitionsScreen
from skating_system.ui.app import SkatingApp


class TestApp(SkatingApp):
    __test__ = False

    def _load_last_event(self) -> None:
        return


def _build_event() -> tuple[SkatingApp, UUID, UUID]:
    app = TestApp()
    event = event_service.create_event("Demo Event")
    judge = event_service.add_participant(event, first_name="J1", last_name="")
    entry = event_service.add_entry(
        event, name="Entry A", members=[EntryMember(participant_id=judge.id)]
    )
    competition_a = event_service.add_competition(
        event,
        name="Comp A",
        judge_ids=[judge.id],
        entry_ids=[entry.id],
    )
    competition_b = event_service.add_competition(
        event,
        name="Comp B",
        judge_ids=[judge.id],
        entry_ids=[entry.id],
    )
    app.event = event
    return app, competition_a.id, competition_b.id


@pytest.mark.asyncio
async def test_delete_competition_soft_deletes_and_hides() -> None:
    app, competition_id, remaining_id = _build_event()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(CompetitionsScreen())
        await pilot.pause()
        screen = cast(CompetitionsScreen, app.screen)
        screen._handle_delete_confirm(competition_id, True)
        await pilot.pause()

        assert app.event is not None
        deleted = event_service.find_competition(app.event, competition_id)
        assert deleted is not None
        assert deleted.is_obsolete is True

        table = screen.query_one("#competitions", DataTable)
        assert table.row_count == 1
        assert screen._selected_competition_id() in {remaining_id, None}


@pytest.mark.asyncio
async def test_delete_competition_cancel_keeps_visible() -> None:
    app, competition_id, _remaining_id = _build_event()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(CompetitionsScreen())
        await pilot.pause()
        screen = cast(CompetitionsScreen, app.screen)
        screen._handle_delete_confirm(competition_id, False)
        await pilot.pause()

        assert app.event is not None
        deleted = event_service.find_competition(app.event, competition_id)
        assert deleted is not None
        assert deleted.is_obsolete is False


@pytest.mark.asyncio
async def test_transcript_panel_hidden_by_default() -> None:
    app, competition_id, _remaining_id = _build_event()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(MatrixScreen(competition_id))
        await pilot.pause()
        screen = cast(MatrixScreen, app.screen)
        assert screen.has_class("sidebar-collapsed")


@pytest.mark.asyncio
async def test_home_table_refreshes_on_resume() -> None:
    app, competition_id, _remaining_id = _build_event()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.push_screen(CompetitionsScreen())
        await pilot.pause()
        screen = cast(CompetitionsScreen, app.screen)

        assert app.event is not None
        competition = event_service.find_competition(app.event, competition_id)
        assert competition is not None
        competition.name = "Renamed"

        screen.on_resume()
        table = screen.query_one("#competitions", DataTable)
        row = table.get_row_at(0)
        assert row[0] == "Renamed"


def test_missing_rank_message_uses_names() -> None:
    app, competition_id, _remaining_id = _build_event()
    event = app.event
    assert event is not None
    competition = event_service.find_competition(event, competition_id)
    assert competition is not None

    screen = MatrixScreen(competition_id)
    errors = screen._friendly_validation_errors(event, competition)

    assert errors
    assert "J1" in errors[0]
    assert str(competition.judge_ids[0]) not in " ".join(errors)
    assert str(competition.entry_ids[0]) not in " ".join(errors)


class ExportApp(App[None]):
    def compose(self):
        yield DataTable(id="table")


@pytest.mark.asyncio
async def test_datatable_to_tsv_text_matches_visible_table() -> None:
    app = ExportApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        table = app.query_one("#table", DataTable)
        table.add_columns("A", "B")
        table.add_row("1", "2")
        table.add_row("3", "4")

        text = datatable_to_tsv_text(table)

    assert text == "A\tB\n1\t2\n3\t4"
