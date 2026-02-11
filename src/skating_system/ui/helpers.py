from __future__ import annotations


def judge_letters(count: int) -> list[str]:
    # reference [S-260210-1.10]
    letters: list[str] = []
    for index in range(count):
        letters.append(_index_to_letter(index))
    return letters


def _index_to_letter(index: int) -> str:
    if index < 0:
        return "?"
    result = ""
    current = index
    while True:
        current, remainder = divmod(current, 26)
        result = chr(ord("A") + remainder) + result
        if current == 0:
            return result
        current -= 1
