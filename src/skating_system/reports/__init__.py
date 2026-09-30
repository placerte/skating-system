"""Generate operational and results PDF documents."""

from skating_system.reports.data import prepare_report_data
from skating_system.reports.call_sheets import generate_call_sheets
from skating_system.reports.generation import ReportGenerationResult
from skating_system.reports.judge_cards import generate_judge_cards
from skating_system.reports.models import CompetitionReportData, EventReportData
from skating_system.reports.pre_event import generate_pre_event_documents
from skating_system.reports.pdf import (
    PdfMetadata,
    PdfTheme,
    build_pdf,
    heading,
    new_page,
    paragraph,
    report_output_path,
    table,
    title,
    vertical_space,
)

__all__ = [
    "CompetitionReportData",
    "EventReportData",
    "PdfMetadata",
    "PdfTheme",
    "build_pdf",
    "generate_call_sheets",
    "generate_judge_cards",
    "generate_pre_event_documents",
    "heading",
    "new_page",
    "paragraph",
    "prepare_report_data",
    "report_output_path",
    "ReportGenerationResult",
    "table",
    "title",
    "vertical_space",
]
