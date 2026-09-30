from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from skating_system.scoring.callback import (
    CallbackMark,
    CallbackPolicy,
    CallbackTally,
    aggregate_callback_marks,
    compute_callback_result,
    normalize_callback_marks,
    select_callback_entries,
)


def _marks(
    entry_ids: list[UUID],
    judge_ids: list[UUID],
    values_by_entry: tuple[tuple[object, ...], ...],
) -> list[CallbackMark]:
    return [
        CallbackMark(judge_id, entry_ids[entry_index], value)
        for entry_index, values in enumerate(values_by_entry)
        for judge_id, value in zip(judge_ids, values, strict=True)
    ]


def test_normalization_accepts_aliases_and_is_independent() -> None:
    entries = [uuid4()]
    judges = [uuid4(), uuid4(), uuid4()]

    normalized, errors = normalize_callback_marks(
        entries,
        judges,
        _marks(entries, judges, ((" yes ", "NO", "Alt"),)),
        alternate_enabled=True,
    )

    assert not errors
    assert normalized is not None
    assert [mark.value for mark in normalized] == ["Y", "N", "A"]


@pytest.mark.parametrize("value", [None, "", "maybe"])
def test_blank_or_unknown_marks_block_results(value: object) -> None:
    entries = [uuid4()]
    judges = [uuid4()]
    result, errors = compute_callback_result(
        entries,
        judges,
        [CallbackMark(judges[0], entries[0], value)],
        CallbackPolicy(alternate_enabled=True, advance_count=1),
    )

    assert result is None
    assert errors


def test_missing_and_duplicate_marks_block_results() -> None:
    entries = [uuid4(), uuid4()]
    judges = [uuid4()]
    duplicate = CallbackMark(judges[0], entries[0], "Y")

    result, errors = compute_callback_result(
        entries,
        judges,
        [duplicate, duplicate],
        CallbackPolicy(alternate_enabled=False, advance_count=1),
    )

    assert result is None
    assert any("Duplicate" in error for error in errors)
    assert any("Missing" in error for error in errors)


def test_alternate_is_rejected_when_disabled() -> None:
    entries = [uuid4()]
    judges = [uuid4()]

    result, errors = compute_callback_result(
        entries,
        judges,
        [CallbackMark(judges[0], entries[0], "A")],
        CallbackPolicy(alternate_enabled=False, advance_count=1),
    )

    assert result is None
    assert any("Alternate is disabled" in error for error in errors)


def test_aggregation_is_independent_and_uses_approved_weights() -> None:
    entries = [uuid4(), uuid4(), uuid4()]
    judges = [uuid4(), uuid4(), uuid4()]
    policy = CallbackPolicy(alternate_enabled=True, advance_count=2)
    normalized, errors = normalize_callback_marks(
        entries,
        judges,
        _marks(entries, judges, (("Y", "Y", "N"), ("Y", "A", "A"), ("N", "N", "N"))),
        alternate_enabled=True,
    )

    assert not errors
    assert normalized is not None
    tallies = aggregate_callback_marks(entries, normalized, policy)
    assert [(item.total, item.yes_count, item.alternate_count) for item in tallies] == [
        (2.0, 2, 0),
        (2.0, 1, 2),
        (0.0, 0, 0),
    ]


def test_selection_uses_yes_then_alternate_as_tie_breakers() -> None:
    entries = [uuid4() for _ in range(4)]
    tallies = (
        CallbackTally(entries[0], 2.0, 2, 0, 1),
        CallbackTally(entries[1], 2.0, 1, 2, 0),
        CallbackTally(entries[2], 1.5, 1, 1, 1),
        CallbackTally(entries[3], 1.5, 1, 0, 2),
    )

    selection = select_callback_entries(tallies, advance_count=3)

    assert selection.advancing_entry_ids == tuple(entries[:3])


def test_boundary_tie_advances_every_tied_entry() -> None:
    entries = [uuid4() for _ in range(4)]
    tallies = (
        CallbackTally(entries[0], 3.0, 3, 0, 0),
        CallbackTally(entries[1], 2.0, 2, 0, 1),
        CallbackTally(entries[2], 2.0, 2, 0, 1),
        CallbackTally(entries[3], 0.0, 0, 0, 3),
    )

    selection = select_callback_entries(tallies, advance_count=2)

    assert selection.advancing_entry_ids == tuple(entries[:3])
    assert selection.boundary_key == (2.0, 2, 0)


@pytest.mark.parametrize(
    ("values", "advance_count", "expected_count"),
    [
        ((("Y", "Y"), ("Y", "Y")), 1, 2),
        ((("N", "N"), ("N", "N")), 1, 2),
        ((("Y", "N"), ("N", "Y"), ("N", "N")), 2, 2),
    ],
    ids=("all-yes", "all-no", "mixed-cutoff"),
)
def test_end_to_end_callback_states(
    values: tuple[tuple[str, ...], ...],
    advance_count: int,
    expected_count: int,
) -> None:
    entries = [uuid4() for _ in values]
    judges = [uuid4() for _ in values[0]]
    policy = CallbackPolicy(
        alternate_enabled=False,
        advance_count=advance_count,
    )

    result, errors = compute_callback_result(
        entries,
        judges,
        _marks(entries, judges, values),
        policy,
    )

    assert not errors
    assert result is not None
    assert len(result.selection.advancing_entry_ids) == expected_count
    assert result.policy == policy
    assert result.policy.ordering == ("total", "yes_count", "alternate_count")


@pytest.mark.parametrize("advance_count", [0, 3])
def test_invalid_cutoff_is_actionable(advance_count: int) -> None:
    entries = [uuid4(), uuid4()]
    judges = [uuid4()]

    result, errors = compute_callback_result(
        entries,
        judges,
        _marks(entries, judges, (("Y",), ("N",))),
        CallbackPolicy(alternate_enabled=False, advance_count=advance_count),
    )

    assert result is None
    assert "advance_count" in " ".join(errors)
