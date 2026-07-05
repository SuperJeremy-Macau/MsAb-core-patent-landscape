from __future__ import annotations

from io import BytesIO
from textwrap import wrap
from typing import Any
import json

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from msab_patent_report.report.models import PatentLandscapeReport, ReportTable


PAGE_WIDTH, PAGE_HEIGHT = letter
LEFT_MARGIN = 54
RIGHT_MARGIN = 54
TOP_MARGIN = 54
BOTTOM_MARGIN = 54
BODY_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
LINE_HEIGHT = 13
TITLE_LINE_HEIGHT = 18


def _cell(value: Any) -> str:
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    return " ".join(str(value).split())


def _safe_filename_text(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")


class _PdfWriter:
    def __init__(self, report: PatentLandscapeReport) -> None:
        self.buffer = BytesIO()
        self.canvas = canvas.Canvas(self.buffer, pagesize=letter, pageCompression=0)
        self.canvas.setTitle(_safe_filename_text(report.title))
        self.y = PAGE_HEIGHT - TOP_MARGIN

    def build(self) -> bytes:
        self.canvas.save()
        return self.buffer.getvalue()

    def _new_page(self) -> None:
        self.canvas.showPage()
        self.y = PAGE_HEIGHT - TOP_MARGIN

    def _ensure_space(self, height: int) -> None:
        if self.y - height < BOTTOM_MARGIN:
            self._new_page()

    def heading(self, text: str, size: int = 14) -> None:
        lines = wrap(_safe_filename_text(text), width=68) or [""]
        self._ensure_space(len(lines) * TITLE_LINE_HEIGHT + 8)
        self.canvas.setFont("Helvetica-Bold", size)
        for line in lines:
            self.canvas.drawString(LEFT_MARGIN, self.y, line)
            self.y -= TITLE_LINE_HEIGHT
        self.y -= 4

    def paragraph(self, text: str, font: str = "Helvetica", size: int = 10, width: int = 95) -> None:
        lines: list[str] = []
        for part in text.splitlines() or [""]:
            lines.extend(wrap(_safe_filename_text(part), width=width) or [""])
        self._ensure_space(max(1, len(lines)) * LINE_HEIGHT + 4)
        self.canvas.setFont(font, size)
        for line in lines:
            self.canvas.drawString(LEFT_MARGIN, self.y, line)
            self.y -= LINE_HEIGHT
        self.y -= 4

    def key_values(self, items: dict[str, Any]) -> None:
        self.canvas.setFont("Helvetica", 9)
        for key, value in items.items():
            text = f"{key}: {_cell(value)}"
            for line in wrap(_safe_filename_text(text), width=100) or [""]:
                self._ensure_space(LINE_HEIGHT)
                self.canvas.drawString(LEFT_MARGIN, self.y, line)
                self.y -= LINE_HEIGHT
        self.y -= 4

    def table(self, table: ReportTable) -> None:
        if not table.rows:
            return
        self.heading(table.title, size=11)
        columns = table.columns
        header = " | ".join(columns)
        self.paragraph(header, font="Helvetica-Bold", size=8, width=110)
        self.canvas.setLineWidth(0.4)
        self._ensure_space(4)
        self.canvas.line(LEFT_MARGIN, self.y, LEFT_MARGIN + BODY_WIDTH, self.y)
        self.y -= 8

        self.canvas.setFont("Helvetica", 8)
        for row in table.rows:
            row_text = " | ".join(_cell(row.get(column, "")) for column in columns)
            for line in wrap(_safe_filename_text(row_text), width=118) or [""]:
                self._ensure_space(11)
                self.canvas.drawString(LEFT_MARGIN, self.y, line)
                self.y -= 11
            self.y -= 2
        self.y -= 4


def report_to_pdf(report: PatentLandscapeReport) -> bytes:
    writer = _PdfWriter(report)

    writer.heading(report.title, size=16)
    writer.paragraph(
        f"Report type: {report.report_type} | Input: {report.input_value} | Generated: {report.generated_at}",
        size=9,
    )

    for section in report.sections:
        writer.heading(section.title)
        writer.paragraph(section.body)
        for table in section.tables:
            writer.table(table)

    writer.heading("Data Provenance")
    writer.key_values(report.provenance)

    writer.heading("Query Row Counts")
    writer.key_values(report.query_row_counts)

    return writer.build()
