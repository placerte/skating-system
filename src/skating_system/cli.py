from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from pathlib import Path

from skating_system.reports import (
    ReportGenerationResult,
    generate_call_sheets,
    generate_judge_cards,
    generate_pre_event_documents,
)
from skating_system.scoring.callback import CallbackResult
from skating_system.services.workbook_compute import compute_workbook
from skating_system.services.skating_scorer import SolveResult
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
    for name, description, handler in (
        ("call-sheets", "Generate competitor call sheets.", _call_sheets_command),
        ("judge-cards", "Generate judge scorecards.", _judge_cards_command),
        ("pre-event", "Generate all pre-event documents.", _pre_event_command),
    ):
        document = generate_commands.add_parser(name, help=description)
        _add_workbook_argument(document)
        document.set_defaults(handler=handler)

    compute = commands.add_parser(
        "compute",
        help="Validate and compute competition results.",
    )
    _add_workbook_argument(compute)
    _add_competition_filter(compute)
    compute.set_defaults(handler=_compute_command)

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


def _call_sheets_command(args: argparse.Namespace) -> int:
    return _print_generation_result(generate_call_sheets(args.workbook))


def _judge_cards_command(args: argparse.Namespace) -> int:
    return _print_generation_result(generate_judge_cards(args.workbook))


def _pre_event_command(args: argparse.Namespace) -> int:
    return _print_generation_result(generate_pre_event_documents(args.workbook))


def _compute_command(args: argparse.Namespace) -> int:
    result = compute_workbook(args.workbook, args.competition)
    for finding in result.findings:
        print(finding.format())
    for computed in result.competitions:
        print(f'COMPETITION: "{computed.competition.name}"')
        if isinstance(computed.result, SolveResult):
            for placement in computed.result.placements:
                label = computed.entry_labels[placement.entry_id]
                print(f"PLACE: {placement.final_place:g} | {label}")
        elif isinstance(computed.result, CallbackResult):
            advancing = set(computed.result.selection.advancing_entry_ids)
            for tally in computed.result.selection.ordered_tallies:
                status = "ADVANCE" if tally.entry_id in advancing else "NOT ADVANCING"
                label = computed.entry_labels[tally.entry_id]
                print(
                    f"CALLBACK: {status} | {tally.total:g} | "
                    f"Y={tally.yes_count} A={tally.alternate_count} | {label}"
                )
            policy = computed.result.policy
            print(
                "POLICY: Y=1 A=0.5 N=0; order=total,yes,alternate; "
                f"advance_count={policy.advance_count}; boundary_ties=advance"
            )
    return 1 if result.has_errors else 0


def _print_generation_result(result: ReportGenerationResult) -> int:
    for output_path in result.output_paths:
        print(f"OUTPUT: {output_path}")
    for finding in result.findings:
        print(finding.format())
    return 1 if result.has_errors else 0


def _pending_command(args: argparse.Namespace) -> int:
    import sys

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
