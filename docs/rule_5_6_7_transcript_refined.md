# Skating System – Transcript Model (Rules 5, 6, 7)

This document refines the desired verbose transcript format for rank attribution
in individual dances under Rules 5, 6, and 7.

The objective is clarity, determinism, and structural consistency.

---

# Terminology Standardization

We standardize the wording used throughout the transcript:

- **Round** → One attempt to attribute a specific rank.
- **Candidates** → The set of entries still unplaced at that moment.
- **Column "1–t" counts** → Number of marks ≤ t (counted, not summed).
- **Column "1–t" sums** → Sum of marks ≤ t (used only in Rule 7).
- **Majority** → floor(judges/2) + 1.
- **Escalation** → Moving from Rule 5 → Rule 6 → Rule 7 → next column.
- **Rank Block** → When multiple candidates are tied and must resolve ranks X..Y together.

---

# RULE 5 – Simple Majority

- Attempting to attribute rank 1:
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

---

# RULE 6 – Greater Majority Tie Break

- Attempting to attribute rank 1:
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

---

# RULE 7 – Equal Majority + Sum Tie Break

- Attempting to attribute rank 1:
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

---

# Structural Notes

1. Every rank attempt begins with a clearly defined candidate set.
2. Column usage must always be explicitly stated.
3. Rule escalation must always be explicitly narrated.
4. Rank blocks must be clearly indicated when multiple positions are resolved together.
5. Final attribution lines must be visually emphasized.

This structure will serve as the canonical transcript reference for implementation.

