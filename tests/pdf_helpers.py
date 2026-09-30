from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PdfInspection:
    """Extracted PDF properties used by report tests."""

    page_count: int
    page_text: tuple[str, ...]
    metadata: dict[str, str]

    @property
    def text(self) -> str:
        return "\n".join(self.page_text)


def inspect_pdf(path: Path) -> PdfInspection:
    """Read a generated PDF and extract page text and public metadata."""

    reader = PdfReader(path)
    metadata = {
        str(key): str(value)
        for key, value in (reader.metadata or {}).items()
        if value is not None
    }
    return PdfInspection(
        page_count=len(reader.pages),
        page_text=tuple(page.extract_text() or "" for page in reader.pages),
        metadata=metadata,
    )
