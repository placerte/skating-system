from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from skating_system.workbook.score_sheets import build_score_sheets
from skating_system.workbook.validation import validate_workbook

CommandHandler = Callable[[argparse.Namespace], int]


# GitHub issue #1: establish the workbook-oriented CLI command surface.
# GitHub issue #17: the retired Textual UI is intentionally not exposed.
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skating-system",
        description="Validate event workbooks, compute results, and generate PDFs.",
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")

    validate = commands.add_parser(
        "validate",
        help="Validate an event workbook.",
    )
    _add_workbook_argument(validate)
    validate.set_defaults(handler=_validate_command)

    build_sheets = commands.add_parser(
        "build-sheets",
        help="Create or refresh score-entry worksheets.",
    )
    _add_workbook_argument(build_sheets)
    build_sheets.add_argument(
        "--rebuild",
        action="store_true",
        help="Allow a destructive rebuild after creating a snapshot.",
    )
    build_sheets.set_defaults(handler=_build_sheets_command)

    generate = commands.add_parser(
        "generate",
        help="Generate pre-competition PDF documents.",
    )
    generate_commands = generate.add_subparsers(
        dest="generate_command",
        metavar="DOCUMENT",
        required=True,
    )
    for name, description, issue in (
        ("call-sheets", "Generate competitor call sheets.", 6),
        ("judge-cards", "Generate judge scorecards.", 7),
        ("pre-event", "Generate all pre-event documents.", 7),
    ):
        document = generate_commands.add_parser(name, help=description)
        _add_workbook_argument(document)
        _set_pending_handler(document, issue=issue)

    compute = commands.add_parser(
        "compute",
        help="Validate and compute competition results.",
    )
    _add_workbook_argument(compute)
    _add_competition_filter(compute)
    _set_pending_handler(compute, issue=12)

    report = commands.add_parser(
        "report",
        help="Generate results reports.",
    )
    report_commands = report.add_subparsers(
        dest="report_command",
        metavar="REPORT",
        required=True,
    )
    for name, description, issue in (
        ("public", "Generate anonymous public results.", 13),
        ("management", "Generate a management audit report.", 14),
        ("mc", "Generate announcement-ready results.", 14),
        ("all", "Generate all results reports.", 14),
    ):
        report_type = report_commands.add_parser(name, help=description)
        _add_workbook_argument(report_type)
        _add_competition_filter(report_type)
        _set_pending_handler(report_type, issue=issue)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler: CommandHandler | None = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0
    return handler(args)


def _add_workbook_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("workbook", type=Path, help="Path to the event .xlsx file.")


def _add_competition_filter(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--competition",
        help="Limit the command to one competition name.",
    )


def _set_pending_handler(parser: argparse.ArgumentParser, *, issue: int) -> None:
    parser.set_defaults(handler=_pending_command, implementation_issue=issue)


def _validate_command(args: argparse.Namespace) -> int:
    report = validate_workbook(args.workbook)
    for finding in report.findings:
        print(finding.format())
    return 1 if report.has_errors else 0


def _build_sheets_command(args: argparse.Namespace) -> int:
    result = build_score_sheets(args.workbook, rebuild=args.rebuild)
    for competition, sheet_name in result.mappings:
        print(f'MAP: "{competition}" -> "{sheet_name}"')
    if result.snapshot_path is not None:
        print(f"SNAPSHOT: {result.snapshot_path}")
    for finding in result.findings:
        print(finding.format())
    return 1 if result.has_errors else 0


def _pending_command(args: argparse.Namespace) -> int:
    command = " ".join(
        value
        for value in (
            args.command,
            getattr(args, "generate_command", None),
            getattr(args, "report_command", None),
        )
        if value is not None
    )
    print(
        f"error: '{command}' is not implemented yet; see GitHub issue "
        f"#{args.implementation_issue}.",
        file=sys.stderr,
    )
    return 2
