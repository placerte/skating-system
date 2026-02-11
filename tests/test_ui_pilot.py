from __future__ import annotations

from pathlib import Path
import re
from typing import cast
from uuid import UUID

import pytest
from textual.widgets import DataTable

from skating_system.domain.models import EntryMember
from skating_system.services import event_service
from skating_system.services.ranking_service import compute_results
from skating_system.ui.app import SkatingApp
from skating_system.ui.screens.competitions import CompetitionsScreen
from skating_system.ui.screens.competition_edit import MatrixScreen

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"
SNAPSHOT_COMPETITIONS = "competitions.txt"
SNAPSHOT_MATRIX = "matrix.txt"
VIEW_SIZE = (120, 36)
DEFAULT_SCREEN_ID = "_default"
TERMINAL_CLASS_PATTERN = re.compile(r"terminal-\d+")
TERMINAL_CLASS_TOKEN = "terminal-TEST"


class TestApp(SkatingApp):
    __test__ = False

    def _load_last_event(self) -> None:
        return


def _build_event() -> tuple[SkatingApp, UUID]:
    app = TestApp()
    event = event_service.create_event("Demo Event")

    judge_a = event_service.add_participant(event, first_name="J1", last_name="")
    judge_b = event_service.add_participant(event, first_name="J2", last_name="")

    entry_a = event_service.add_entry(
        event, name="Entry A", members=[EntryMember(participant_id=judge_a.id)]
    )
    entry_b = event_service.add_entry(
        event, name="Entry B", members=[EntryMember(participant_id=judge_b.id)]
    )

    competition = event_service.add_competition(
        event,
        name="Comp 1",
        judge_ids=[judge_a.id, judge_b.id],
        entry_ids=[entry_a.id, entry_b.id],
    )

    event_service.set_rank_mark(
        event, competition.id, judge_id=judge_a.id, entry_id=entry_a.id, rank=1
    )
    event_service.set_rank_mark(
        event, competition.id, judge_id=judge_a.id, entry_id=entry_b.id, rank=2
    )
    event_service.set_rank_mark(
        event, competition.id, judge_id=judge_b.id, entry_id=entry_a.id, rank=2
    )
    event_service.set_rank_mark(
        event, competition.id, judge_id=judge_b.id, entry_id=entry_b.id, rank=1
    )

    result, errors = compute_results(competition)
    assert not errors
    assert result is not None

    app.event = event
    app.set_competition_result(competition.id, result)
    return app, competition.id


def _load_snapshot(name: str) -> str:
    return (SNAPSHOT_DIR / name).read_text(encoding="utf-8")


def _normalize_snapshot(svg: str) -> str:
    return TERMINAL_CLASS_PATTERN.sub(TERMINAL_CLASS_TOKEN, svg)


def _assert_snapshot(actual: str, name: str) -> None:
    expected = _load_snapshot(name)
    assert _normalize_snapshot(actual) == expected


async def _ensure_competitions_screen(app: SkatingApp, pilot) -> None:
    if app.screen.id == DEFAULT_SCREEN_ID:
        app.push_screen(CompetitionsScreen())
        await pilot.pause()


@pytest.mark.asyncio
async def test_competitions_screen_snapshot() -> None:
    app, _ = _build_event()
    async with app.run_test(size=VIEW_SIZE) as pilot:
        await pilot.pause()
        await _ensure_competitions_screen(app, pilot)
        snapshot = app.export_screenshot(simplify=True)
        _assert_snapshot(snapshot, SNAPSHOT_COMPETITIONS)


@pytest.mark.asyncio
async def test_matrix_screen_snapshot() -> None:
    app, _ = _build_event()
    async with app.run_test(size=VIEW_SIZE) as pilot:
        await pilot.pause()
        await _ensure_competitions_screen(app, pilot)
        table = app.screen.query_one("#competitions", DataTable)
        table.focus()
        table.move_cursor(row=0, column=0)
        screen = cast(CompetitionsScreen, app.screen)
        screen.action_open()
        await pilot.pause()
        snapshot = app.export_screenshot(simplify=True)
        _assert_snapshot(snapshot, SNAPSHOT_MATRIX)


@pytest.mark.asyncio
async def test_ui_monkey_smoke() -> None:
    app, _ = _build_event()
    async with app.run_test(size=VIEW_SIZE) as pilot:
        await pilot.pause()
        await _ensure_competitions_screen(app, pilot)
        table = app.screen.query_one("#competitions", DataTable)
        table.focus()
        table.move_cursor(row=0, column=0)
        screen = cast(CompetitionsScreen, app.screen)
        screen.action_open()
        await pilot.pause()
        await pilot.press("c")
        await pilot.press("C")
        await pilot.press("r")
        await pilot.press(*list("Renamed"))
        await pilot.press("enter")
        await pilot.press("escape")


@pytest.mark.asyncio
async def test_add_entry_does_not_crash_with_stale_results() -> None:
    app, competition_id = _build_event()
    async with app.run_test(size=VIEW_SIZE) as pilot:
        app.push_screen(MatrixScreen(competition_id))
        await pilot.pause()
        screen = cast(MatrixScreen, app.screen)
        screen._handle_add_entry_name("101 Joe")
        await pilot.pause()
        assert app.event is not None
        competition = event_service.find_competition(app.event, competition_id)
        assert competition is not None
        assert len(competition.entry_ids) == 3
