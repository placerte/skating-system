from __future__ import annotations

import pyfiglet


def render_figlet(text: str, *, font: str, width: int, align: str = "left") -> str:
    safe_width = max(1, width)
    rendered = pyfiglet.figlet_format(text, font=font, width=safe_width)
    lines = _strip_blank_lines(rendered.splitlines())
    max_len = max(len(line) for line in lines)
    if align == "center":
        padding = max(0, (safe_width - max_len) // 2)
        centered = [" " * padding + line.rstrip().ljust(max_len) for line in lines]
        return "\n".join(centered)
    if align == "right":
        padding = max(0, safe_width - max_len)
        aligned = [" " * padding + line.rstrip().ljust(max_len) for line in lines]
        return "\n".join(aligned)
    return "\n".join(line.rstrip() for line in lines)


def _strip_blank_lines(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return [""]
    return lines
