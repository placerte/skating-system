from __future__ import annotations

import os
import tempfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

PAGE_WIDTH, PAGE_HEIGHT = letter
DEFAULT_MARGIN: Final = 0.55 * inch
FOOTER_HEIGHT: Final = 0.25 * inch


@dataclass(frozen=True)
class PdfMetadata:
    """Stable public PDF metadata fields."""

    title: str
    subject: str = ""
    author: str = "Skating System"
    creator: str = "skating-system"


@dataclass(frozen=True)
class PdfTheme:
    """Small set of shared report layout values."""

    page_size: tuple[float, float] = letter
    left_margin: float = DEFAULT_MARGIN
    right_margin: float = DEFAULT_MARGIN
    top_margin: float = DEFAULT_MARGIN
    bottom_margin: float = DEFAULT_MARGIN + FOOTER_HEIGHT


class _InvariantCanvas(Canvas):
    def __init__(self, *args: object, **kwargs: object) -> None:
        kwargs["invariant"] = 1
        kwargs["pageCompression"] = 1
        super().__init__(*args, **kwargs)


# GitHub issue #5: shared deterministic PDF generation primitives.
def build_pdf(
    output_path: Path,
    elements: Iterable[Flowable],
    *,
    metadata: PdfMetadata,
    theme: PdfTheme | None = None,
) -> Path:
    """Build a deterministic PDF and atomically replace the target file."""

    if output_path.suffix.casefold() != ".pdf":
        raise ValueError("PDF output path must end with .pdf.")
    active_theme = theme or PdfTheme()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.stem}.",
        suffix=".pdf",
        dir=output_path.parent,
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        document = _document(temporary_path, metadata, active_theme)
        document.build(list(elements), canvasmaker=_InvariantCanvas)
        if output_path.exists():
            temporary_path.chmod(output_path.stat().st_mode)
        os.replace(temporary_path, output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return output_path


def report_output_path(
    workbook_path: Path,
    filename: str,
    *,
    output_dir: Path | None = None,
) -> Path:
    """Return a deterministic report path without creating it."""

    if (
        not filename
        or Path(filename).name != filename
        or "/" in filename
        or "\\" in filename
    ):
        raise ValueError("Report filename must be a plain filename.")
    normalized_filename = (
        filename if filename.casefold().endswith(".pdf") else f"{filename}.pdf"
    )
    directory = (
        output_dir if output_dir is not None else workbook_path.parent / "reports"
    )
    return directory / normalized_filename


def title(text: str) -> Paragraph:
    """Create a shared report title."""

    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        "SkatingTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=12,
    )
    return Paragraph(_escape(text), style)


def heading(text: str) -> Paragraph:
    """Create a shared section heading."""

    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        "SkatingHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        spaceBefore=6,
        spaceAfter=6,
    )
    return Paragraph(_escape(text), style)


def paragraph(text: str) -> Paragraph:
    """Create a body paragraph with escaped plain text."""

    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        "SkatingBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        spaceAfter=6,
    )
    return Paragraph(_escape(text), style)


def table(
    headers: Sequence[str],
    rows: Iterable[Sequence[object]],
    *,
    column_widths: Sequence[float] | None = None,
    repeat_header: bool = True,
) -> Table:
    """Create a legible table that can split across pages."""

    data = [[paragraph_cell(value) for value in headers]]
    data.extend([paragraph_cell(value) for value in row] for row in rows)
    result = Table(
        data,
        colWidths=list(column_widths) if column_widths is not None else None,
        repeatRows=1 if repeat_header else 0,
        hAlign="LEFT",
    )
    result.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6E6E6")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#777777")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return result


def paragraph_cell(value: object) -> Paragraph:
    """Convert one plain table value to a safely escaped paragraph."""

    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        "SkatingTableCell",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
    )
    return Paragraph(_escape("" if value is None else str(value)), style)


def vertical_space(points: float = 6) -> Spacer:
    """Create predictable vertical space between flowables."""

    return Spacer(1, points)


def new_page() -> PageBreak:
    """Start the following content on a new page."""

    return PageBreak()


def _document(
    path: Path,
    metadata: PdfMetadata,
    theme: PdfTheme,
) -> BaseDocTemplate:
    page_width, page_height = theme.page_size
    document = BaseDocTemplate(
        str(path),
        pagesize=theme.page_size,
        leftMargin=theme.left_margin,
        rightMargin=theme.right_margin,
        topMargin=theme.top_margin,
        bottomMargin=theme.bottom_margin,
        title=metadata.title,
        author=metadata.author,
        subject=metadata.subject,
        creator=metadata.creator,
    )
    frame = Frame(
        theme.left_margin,
        theme.bottom_margin,
        page_width - theme.left_margin - theme.right_margin,
        page_height - theme.top_margin - theme.bottom_margin,
        id="content",
    )
    document.addPageTemplates(
        [PageTemplate(id="standard", frames=[frame], onPage=_draw_page_footer)]
    )
    return document


def _draw_page_footer(canvas: Canvas, document: BaseDocTemplate) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawCentredString(
        document.pagesize[0] / 2,
        0.35 * inch,
        f"Page {document.page}",
    )
    canvas.restoreState()


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
