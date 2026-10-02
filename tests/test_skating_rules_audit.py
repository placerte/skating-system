from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import pytest

from skating_system.domain.models import Competition, RankMark
from skating_system.services.skating_scorer import compute_solve_result


@dataclass(frozen=True)
class OfficialExample:
    rule: int
    labels: tuple[str, ...]
    marks: tuple[tuple[int, ...], ...]
    counts: tuple[tuple[int, ...], ...]
    sums: tuple[tuple[int, ...], ...]


# GitHub issue #8: independently transcribed WDSF/SDF Rules 5-8 examples.
OFFICIAL_EXAMPLES = (
    OfficialExample(
        rule=5,
        labels=("51", "52", "53", "54", "55", "56"),
        marks=(
            (1, 1, 1, 2, 1),
            (4, 2, 2, 1, 2),
            (3, 3, 3, 5, 4),
            (2, 4, 5, 4, 3),
            (5, 6, 4, 3, 5),
            (6, 5, 6, 6, 6),
        ),
        counts=(
            (4, 5, 5, 5, 5, 5),
            (1, 4, 4, 5, 5, 5),
            (0, 0, 3, 4, 5, 5),
            (0, 1, 2, 4, 5, 5),
            (0, 0, 1, 2, 4, 5),
            (0, 0, 0, 0, 1, 5),
        ),
        sums=(
            (4, 6, 6, 6, 6, 6),
            (1, 7, 7, 11, 11, 11),
            (0, 0, 9, 13, 18, 18),
            (0, 2, 5, 13, 18, 18),
            (0, 0, 3, 7, 17, 23),
            (0, 0, 0, 0, 5, 29),
        ),
    ),
    OfficialExample(
        rule=6,
        labels=("61", "62", "63", "64", "65", "66"),
        marks=(
            (1, 1, 2, 1, 4, 2, 1),
            (6, 2, 1, 5, 2, 1, 2),
            (2, 4, 3, 3, 6, 3, 3),
            (3, 3, 5, 2, 1, 5, 4),
            (4, 5, 6, 4, 3, 6, 5),
            (5, 6, 4, 6, 5, 4, 6),
        ),
        counts=(
            (4, 6, 6, 7, 7, 7),
            (2, 5, 5, 5, 6, 7),
            (0, 1, 5, 6, 6, 7),
            (1, 2, 4, 5, 7, 7),
            (0, 0, 1, 3, 5, 7),
            (0, 0, 0, 2, 4, 7),
        ),
        sums=(
            (4, 8, 8, 12, 12, 12),
            (2, 8, 8, 8, 13, 19),
            (0, 2, 14, 18, 18, 24),
            (1, 3, 9, 13, 23, 23),
            (0, 0, 3, 11, 21, 33),
            (0, 0, 0, 8, 18, 36),
        ),
    ),
    OfficialExample(
        rule=7,
        labels=("71", "72", "73", "74", "75", "76"),
        marks=(
            (3, 1, 6, 1, 1, 2, 1),
            (2, 2, 1, 5, 3, 1, 3),
            (1, 5, 4, 2, 2, 6, 2),
            (5, 4, 2, 4, 6, 5, 4),
            (4, 6, 3, 3, 5, 4, 6),
            (6, 3, 5, 6, 4, 3, 5),
        ),
        counts=(
            (4, 5, 6, 6, 6, 7),
            (2, 4, 6, 6, 7, 7),
            (1, 4, 4, 5, 6, 7),
            (0, 1, 1, 4, 6, 7),
            (0, 0, 2, 4, 5, 7),
            (0, 0, 2, 3, 5, 7),
        ),
        sums=(
            (4, 6, 9, 9, 9, 15),
            (2, 6, 12, 12, 17, 17),
            (1, 7, 7, 11, 16, 22),
            (0, 2, 2, 14, 24, 30),
            (0, 0, 6, 14, 19, 31),
            (0, 0, 6, 10, 20, 32),
        ),
    ),
    OfficialExample(
        rule=8,
        labels=("81", "82", "83", "84", "85", "86"),
        marks=(
            (3, 3, 3, 2, 5, 2, 3),
            (4, 4, 4, 3, 2, 3, 2),
            (2, 2, 6, 6, 4, 1, 4),
            (1, 6, 1, 5, 1, 4, 6),
            (5, 5, 5, 1, 3, 6, 1),
            (6, 1, 2, 4, 6, 5, 5),
        ),
        counts=(
            (0, 2, 6, 6, 7, 7),
            (0, 2, 4, 7, 7, 7),
            (1, 3, 3, 5, 5, 7),
            (3, 3, 3, 4, 5, 7),
            (2, 2, 3, 3, 6, 7),
            (1, 2, 2, 3, 5, 7),
        ),
        sums=(
            (0, 4, 16, 16, 21, 21),
            (0, 4, 10, 22, 22, 22),
            (1, 5, 5, 13, 13, 25),
            (3, 3, 3, 7, 12, 24),
            (2, 2, 5, 5, 20, 26),
            (1, 3, 3, 7, 17, 29),
        ),
    ),
)


@pytest.mark.parametrize(
    "example", OFFICIAL_EXAMPLES, ids=lambda item: f"rule-{item.rule}"
)
def test_official_rules_5_to_8_examples(example: OfficialExample) -> None:
    judge_ids = [uuid4() for _ in range(len(example.marks[0]))]
    entry_ids = [uuid4() for _ in example.labels]
    marks = [
        RankMark(judge_id, entry_ids[entry_index], rank)
        for entry_index, entry_marks in enumerate(example.marks)
        for judge_id, rank in zip(judge_ids, entry_marks, strict=True)
    ]
    competition = Competition(
        id=uuid4(),
        name=f"Official Rule {example.rule} example",
        judge_ids=judge_ids,
        entry_ids=entry_ids,
        rank_marks=marks,
    )

    result, errors = compute_solve_result(competition)

    assert not errors
    assert result is not None
    assert result.derived_table.majority_threshold == len(judge_ids) // 2 + 1
    assert [placement.final_place for placement in result.placements] == [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
    ]
    assert [placement.entry_id for placement in result.placements] == entry_ids
    assert (
        tuple(
            tuple(result.derived_table.counts_by_entry[entry_id])
            for entry_id in entry_ids
        )
        == example.counts
    )
    assert (
        tuple(
            tuple(result.derived_table.sums_by_entry[entry_id])
            for entry_id in entry_ids
        )
        == example.sums
    )


def test_even_judge_panel_is_rejected() -> None:
    judge_ids = [uuid4() for _ in range(2)]
    entry_ids = [uuid4() for _ in range(2)]
    competition = Competition(
        id=uuid4(),
        name="Invalid even panel",
        judge_ids=judge_ids,
        entry_ids=entry_ids,
        rank_marks=[
            RankMark(judge_ids[0], entry_ids[0], 1),
            RankMark(judge_ids[0], entry_ids[1], 2),
            RankMark(judge_ids[1], entry_ids[0], 2),
            RankMark(judge_ids[1], entry_ids[1], 1),
        ],
    )

    result, errors = compute_solve_result(competition)

    assert result is None
    assert "odd number of judges" in " ".join(errors)


def test_official_three_way_terminal_tie_outcome() -> None:
    """The federation text says places 3–5 share 4.0 when inseparable.

    The source gives the outcome but no ballot matrix. This derived matrix keeps
    the first two entries unanimous, while the last three receive identical
    rank distributions and therefore remain tied through the final column.
    """

    judge_ids = [uuid4() for _ in range(3)]
    entry_ids = [uuid4() for _ in range(5)]
    marks_by_entry = (
        (1, 1, 1),
        (2, 2, 2),
        (3, 4, 5),
        (4, 5, 3),
        (5, 3, 4),
    )
    competition = Competition(
        id=uuid4(),
        name="Derived ballot for official three-way terminal tie",
        judge_ids=judge_ids,
        entry_ids=entry_ids,
        rank_marks=[
            RankMark(judge_id, entry_ids[entry_index], rank)
            for entry_index, entry_marks in enumerate(marks_by_entry)
            for judge_id, rank in zip(judge_ids, entry_marks, strict=True)
        ],
    )

    result, errors = compute_solve_result(competition)

    assert not errors
    assert result is not None
    placements = {item.entry_id: item.final_place for item in result.placements}
    assert placements[entry_ids[0]] == 1.0
    assert placements[entry_ids[1]] == 2.0
    assert {placements[entry_id] for entry_id in entry_ids[2:]} == {4.0}


# Independently entered from seven physical Short Showcase judge sheets by the
# event owner, then compared with the first-pass image transcription.
def test_retro_boreal_2026_short_showcase_reconstruction() -> None:
    labels = (
        "Yanik & Sydjie",
        "Philippe & Caroline",
        "Sébastien & Miriook",
        "Nathaniel & Geneviève",
        "Annie & Ludovic",
        "Karell & Guillaume",
        "Jimmy & Myriam",
        "Florence & Anthony",
        "Sydjie & Philippe",
    )
    marks_by_entry = (
        (9, 8, 9, 1, 1, 1, 3),
        (7, 2, 8, 6, 3, 2, 2),
        (3, 3, 2, 2, 9, 6, 9),
        (5, 1, 1, 4, 2, 9, 7),
        (4, 5, 5, 3, 7, 3, 8),
        (6, 7, 6, 9, 4, 8, 6),
        (1, 6, 4, 8, 6, 5, 1),
        (2, 4, 3, 7, 8, 4, 4),
        (8, 9, 7, 5, 5, 7, 5),
    )
    expected = {
        "Yanik & Sydjie": 1.0,
        "Philippe & Caroline": 2.0,
        "Sébastien & Miriook": 3.0,
        "Florence & Anthony": 4.0,
        "Nathaniel & Geneviève": 5.0,
        "Jimmy & Myriam": 6.0,
        "Annie & Ludovic": 7.0,
        "Karell & Guillaume": 8.5,
        "Sydjie & Philippe": 8.5,
    }
    judge_ids = [uuid4() for _ in range(7)]
    entry_ids = [uuid4() for _ in labels]
    competition = Competition(
        id=uuid4(),
        name="Rétro Boréale 2026 Short Showcase",
        judge_ids=judge_ids,
        entry_ids=entry_ids,
        rank_marks=[
            RankMark(judge_id, entry_ids[entry_index], rank)
            for entry_index, entry_marks in enumerate(marks_by_entry)
            for judge_id, rank in zip(judge_ids, entry_marks, strict=True)
        ],
    )

    result, errors = compute_solve_result(competition)

    assert not errors
    assert result is not None
    actual = {
        labels[entry_ids.index(placement.entry_id)]: placement.final_place
        for placement in result.placements
    }
    assert actual == expected
