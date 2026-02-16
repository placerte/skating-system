from __future__ import annotations

from uuid import uuid4

from skating_system.domain.models import Competition, RankMark
from skating_system.services.skating_scorer import (
    compute_solve_result,
    render_transcript,
)


RULE_5_TRANSCRIPT = """- Attempting to attribute rank 1:
  - Candidates entering this round: 101, 102, 103, 104, 105, 106
  - Using column "1" counts
  - Rule 5 – Majority found: 101 (alone)
  - **Rank 1 attributed to 101**

- Attempting to attribute rank 2:
  - Candidates entering this round: 102, 103, 104, 105, 106
  - Using column "1–2" counts
  - Rule 5 – Majority found: 102 (alone)
  - **Rank 2 attributed to 102**

- Attempting to attribute rank 3:
  - Candidates entering this round: 103, 104, 105, 106
  - Using column "1–3" counts
  - Rule 5 – Majority found: 103 (alone)
  - **Rank 3 attributed to 103**

- Attempting to attribute rank 4:
  - Candidates entering this round: 104, 105, 106
  - Using column "1–4" counts
  - Rule 5 – Majority found: 104 (alone)
  - **Rank 4 attributed to 104**

- Attempting to attribute rank 5:
  - Candidates entering this round: 105, 106
  - Using column "1–5" counts
  - Rule 5 – Majority found: 105 (alone)
  - **Rank 5 attributed to 105**

- Attempting to attribute rank 6:
  - Candidates entering this round: 106 (alone)
  - **Rank 6 attributed to 106**
"""


RULE_6_TRANSCRIPT = """- Attempting to attribute rank 1:
  - Candidates entering this round: 101, 102, 103, 104, 105, 106
  - Using column "1" counts
  - Rule 5 – Majority found: 101 (alone)
  - **Rank 1 attributed to 101**

- Attempting to attribute rank 2:
  - Candidates entering this round: 102, 103, 104, 105, 106
  - Using column "1–2" counts
  - Rule 5 – Majority found: 102 (alone)
  - **Rank 2 attributed to 102**

- Attempting to attribute rank 3:
  - Candidates entering this round: 103, 104, 105, 106
  - Using column "1–3" counts
  - Rule 5 – Majority tie: 103 and 104
  - Rank block detected for ranks 3 and 4

    - Resolving rank 3 within block:
      - Candidates: 103, 104
      - Using column "1–3" counts
      - Rule 6 – Greater majority: 103 (alone)
      - **Rank 3 attributed to 103**

    - Resolving rank 4 within block:
      - Candidates: 104 (alone)
      - **Rank 4 attributed to 104**

- Attempting to attribute rank 5:
  - Candidates entering this round: 105, 106
  - Using column "1–4" counts
  - Rule 5 – No majority found
  - Escalating to column "1–5" counts
  - Rule 5 – Majority tie: 105 and 106
  - Rank block detected for ranks 5 and 6

    - Resolving rank 5 within block:
      - Candidates: 105, 106
      - Using column "1–5" counts
      - Rule 6 – Greater majority: 105 (alone)
      - **Rank 5 attributed to 105**

    - Resolving rank 6 within block:
      - Candidates: 106 (alone)
      - **Rank 6 attributed to 106**
"""


RULE_7_TRANSCRIPT = """- Attempting to attribute rank 1:
  - Candidates entering this round: 101, 102, 103, 104, 105, 106
  - Using column "1" counts
  - Rule 5 – Majority found: 101 (alone)
  - **Rank 1 attributed to 101**

- Attempting to attribute rank 2:
  - Candidates entering this round: 102, 103, 104, 105, 106
  - Using column "1–2" counts
  - Rule 5 – Majority tie: 102 and 103
  - Rank block detected for ranks 2 and 3

    - Resolving rank 2 within block:
      - Candidates: 102, 103
      - Using column "1–2" counts
      - Rule 6 – Equal majority persists
      - Escalating to Rule 7 (sum comparison)
      - Using column "1–2" sums
      - Rule 7 – Smaller sum: 102 (alone)
      - **Rank 2 attributed to 102**

    - Resolving rank 3 within block:
      - Candidates: 103 (alone)
      - **Rank 3 attributed to 103**

- Attempting to attribute rank 4:
  - Candidates entering this round: 104, 105, 106
  - Using column "1–3" counts
  - Rule 5 – No majority found
  - Escalating to column "1–4" counts
  - Rule 5 – Majority tie: 104 and 105
  - Rank block detected for ranks 4 and 5

    - Resolving rank 4 within block:
      - Candidates: 104, 105
      - Using column "1–4" counts
      - Rule 6 – Equal majority persists
      - Escalating to Rule 7 (sum comparison)
      - Using column "1–4" sums
      - Rule 7 – Equal sum persists
      - Escalating to next column "1–5" counts
      - Rule 5 – Majority tie persists
      - Rule 6 – Greater majority: 104 (alone)
      - **Rank 4 attributed to 104**

    - Resolving rank 5 within block:
      - Candidates: 105 (alone)
      - **Rank 5 attributed to 105**

- Attempting to attribute rank 6:
  - Candidates entering this round: 106 (alone)
  - **Rank 6 attributed to 106**
"""


def _build_competition(
    *,
    judge_count: int,
    entry_labels: list[str],
    marks_by_entry: list[list[int]],
    name: str,
) -> tuple[Competition, dict]:
    judges = [uuid4() for _ in range(judge_count)]
    entries = [uuid4() for _ in entry_labels]

    rank_marks: list[RankMark] = []
    for judge_index, judge_id in enumerate(judges):
        for entry_index, entry_id in enumerate(entries):
            rank = marks_by_entry[entry_index][judge_index]
            rank_marks.append(RankMark(judge_id, entry_id, rank))

    competition = Competition(
        id=uuid4(),
        name=name,
        judge_ids=judges,
        entry_ids=entries,
        rank_marks=rank_marks,
    )
    labels = {entry_id: label for entry_id, label in zip(entries, entry_labels)}
    return competition, labels


def test_transcript_rule_5_fixture() -> None:
    marks_by_entry = [
        [1, 1, 1, 2, 1],
        [4, 2, 2, 1, 2],
        [3, 3, 3, 5, 4],
        [2, 4, 5, 4, 3],
        [5, 6, 4, 3, 5],
        [6, 5, 6, 6, 6],
    ]
    competition, labels = _build_competition(
        judge_count=5,
        entry_labels=["101", "102", "103", "104", "105", "106"],
        marks_by_entry=marks_by_entry,
        name="Rule 5",
    )

    result, errors = compute_solve_result(competition, entry_labels=labels)
    assert not errors
    assert result is not None

    transcript = render_transcript(result.transcript_root)
    assert transcript == RULE_5_TRANSCRIPT


def test_transcript_rule_6_fixture() -> None:
    marks_by_entry = [
        [1, 1, 2, 1, 4, 2, 1],
        [6, 2, 1, 5, 2, 1, 2],
        [2, 4, 3, 3, 6, 3, 3],
        [3, 3, 5, 2, 1, 5, 4],
        [4, 5, 6, 4, 3, 6, 5],
        [5, 6, 4, 6, 5, 4, 6],
    ]
    competition, labels = _build_competition(
        judge_count=7,
        entry_labels=["101", "102", "103", "104", "105", "106"],
        marks_by_entry=marks_by_entry,
        name="Rule 6",
    )

    result, errors = compute_solve_result(competition, entry_labels=labels)
    assert not errors
    assert result is not None

    transcript = render_transcript(result.transcript_root)
    assert transcript == RULE_6_TRANSCRIPT


def test_transcript_rule_7_fixture() -> None:
    marks_by_entry = [
        [3, 1, 6, 1, 1, 2, 1],
        [2, 2, 1, 5, 3, 1, 3],
        [1, 5, 4, 2, 2, 6, 2],
        [5, 4, 2, 4, 6, 5, 4],
        [4, 6, 3, 3, 5, 4, 6],
        [6, 3, 5, 6, 4, 3, 5],
    ]
    competition, labels = _build_competition(
        judge_count=7,
        entry_labels=["101", "102", "103", "104", "105", "106"],
        marks_by_entry=marks_by_entry,
        name="Rule 7",
    )

    result, errors = compute_solve_result(competition, entry_labels=labels)
    assert not errors
    assert result is not None

    transcript = render_transcript(result.transcript_root)
    assert transcript == RULE_7_TRANSCRIPT
