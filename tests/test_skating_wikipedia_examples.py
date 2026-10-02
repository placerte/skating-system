from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import pytest

from skating_system.domain.models import Competition, RankMark
from skating_system.services.skating_scorer import compute_solve_result


@dataclass(frozen=True)
class WikipediaExample:
    marks: tuple[tuple[int, ...], ...]
    expected_places: tuple[float, ...]


# Secondary-source regression matrices transcribed from Wikipedia's
# "Skating system" article, revision oldid=1067820918 (2022-01-25).
WIKIPEDIA_EXAMPLES = {
    "clear-majority": WikipediaExample(
        marks=((1, 1, 2, 1, 2), (2, 2, 1, 3, 1), (3, 3, 3, 2, 3)),
        expected_places=(1.0, 2.0, 3.0),
    ),
    "multiple-majorities": WikipediaExample(
        marks=(
            (1, 1, 1, 5, 2),
            (2, 3, 3, 1, 1),
            (3, 2, 2, 2, 5),
            (4, 4, 5, 3, 3),
            (5, 5, 4, 4, 4),
        ),
        expected_places=(1.0, 2.0, 3.0, 4.0, 5.0),
    ),
    "no-majority": WikipediaExample(
        marks=((1, 1, 2, 2, 3), (2, 2, 1, 1, 2), (3, 3, 3, 3, 1)),
        expected_places=(2.0, 1.0, 3.0),
    ),
    "shared-place-and-second-place-winner": WikipediaExample(
        marks=(
            (1, 1, 3, 3, 4),
            (2, 2, 2, 2, 2),
            (3, 3, 4, 1, 1),
            (4, 4, 1, 4, 3),
        ),
        expected_places=(2.5, 1.0, 2.5, 4.0),
    ),
    "tied-subgroup-only": WikipediaExample(
        marks=(
            (1, 1, 1, 2, 5),
            (2, 4, 5, 1, 2),
            (5, 2, 2, 5, 1),
            (3, 3, 3, 3, 3),
            (4, 5, 4, 4, 4),
        ),
        expected_places=(1.0, 2.0, 3.0, 4.0, 5.0),
    ),
}


@pytest.mark.parametrize(
    "example",
    WIKIPEDIA_EXAMPLES.values(),
    ids=WIKIPEDIA_EXAMPLES.keys(),
)
def test_wikipedia_single_dance_examples(example: WikipediaExample) -> None:
    judge_ids = [uuid4() for _ in example.marks[0]]
    entry_ids = [uuid4() for _ in example.marks]
    competition = Competition(
        id=uuid4(),
        name="Wikipedia secondary-source regression",
        judge_ids=judge_ids,
        entry_ids=entry_ids,
        rank_marks=[
            RankMark(judge_id, entry_ids[entry_index], rank)
            for entry_index, entry_marks in enumerate(example.marks)
            for judge_id, rank in zip(judge_ids, entry_marks, strict=True)
        ],
    )

    result, errors = compute_solve_result(competition)

    assert not errors
    assert result is not None
    actual_places = {
        placement.entry_id: placement.final_place for placement in result.placements
    }
    assert tuple(actual_places[entry_id] for entry_id in entry_ids) == (
        example.expected_places
    )
