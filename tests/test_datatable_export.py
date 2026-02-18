from __future__ import annotations

from pathlib import Path

import pytest
from rich.text import Text
from textual.app import App
from textual.widgets import DataTable

from skating_system.ui.datatable_export import export_datatable_to_csv


class ExportApp(App[None]):
    def compose(self):
        yield DataTable(id="table")


@pytest.mark.asyncio
async def test_export_datatable_to_csv(tmp_path: Path) -> None:
    app = ExportApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        table = app.query_one("#table", DataTable)
        table.add_columns("A", "B")
        table.add_row(Text("Hello"), "2")
        table.add_row("3", "4")

        output_path = tmp_path / "export.csv"
        export_datatable_to_csv(table, output_path)

    content = output_path.read_text(encoding="utf-8").splitlines()
    assert content == ["A,B", "Hello,2", "3,4"]
