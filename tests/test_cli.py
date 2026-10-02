from __future__ import annotations

import pytest

from skating_system.cli import build_parser, main


def test_root_help_describes_workbook_workflow(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([]) == 0

    output = capsys.readouterr().out
    assert "validate" in output
    assert "build-sheets" in output
    assert "generate" in output
    assert "compute" in output
    assert "report" in output
    assert "legacy-ui" not in output


def test_report_command_fails_clearly_for_missing_workbook(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["report", "management", "event.xlsx"]) == 1

    output = capsys.readouterr().out
    assert "Could not open workbook" in output


def test_compute_accepts_competition_filter() -> None:
    args = build_parser().parse_args(
        ["compute", "event.xlsx", "--competition", "Open Mix & Match"]
    )

    assert args.competition == "Open Mix & Match"


@pytest.mark.parametrize("command", ["generate", "report"])
def test_nested_command_is_required(command: str) -> None:
    with pytest.raises(SystemExit) as error:
        main([command])

    assert error.value.code == 2
