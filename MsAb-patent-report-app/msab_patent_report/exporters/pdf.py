from __future__ import annotations

from io import BytesIO
from typing import Any
import json

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from msab_patent_report.branding import PDF_WATERMARK_TEXT, SOURCE_NOTE
from msab_patent_report.report.models import PatentLandscapeReport, ReportTable


SUMMARY_LABELS = {
    "patent_count": "Patent publications",
    "family_count": "Patent families",
    "target_pair_count": "Target pairs",
    "target_count": "Targets",
    "assignee_count": "Assignees",
    "first_year": "First year",
    "latest_year": "Latest year",
}

CHART_SPECS = (
    ("Publication trend", "yearly_trend", "year", "patent_count", "line"),
    ("Top assignees", "top_assignees", "assignee", "patent_count", "barh"),
    ("Top target pairs", "top_target_pairs", "target_pair", "patent_count", "barh"),
    ("Top targets", "top_targets", "target", "patent_count", "barh"),
)


def _cell(value: Any) -> str:
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    return " ".join(str(value).split())


def _pdf_safe(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _truncate(text: str, limit: int = 220) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "..."


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "MsabTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            spaceAfter=8,
        ),
        "meta": ParagraphStyle(
            "MsabMeta",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#5d6878"),
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "MsabH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=15,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "h3": ParagraphStyle(
            "MsabH3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            spaceBefore=5,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "MsabBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "MsabSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=8.4,
        ),
        "table_header": ParagraphStyle(
            "MsabTableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=8.5,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1a2638"),
        ),
        "table_cell": ParagraphStyle(
            "MsabTableCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=6.8,
            leading=8.1,
        ),
    }


def _paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_pdf_safe(_cell(text)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), style)


def _metric_table(report: PatentLandscapeReport, styles: dict[str, ParagraphStyle], width: float) -> Table | None:
    summary = (report.query_results.get("summary") or [{}])[0]
    items = [(SUMMARY_LABELS[key], summary[key]) for key in SUMMARY_LABELS if key in summary]
    if not items:
        return None

    rows = []
    for start in range(0, len(items), 4):
        cells = []
        for label, value in items[start : start + 4]:
            cells.append(
                [
                    _paragraph(label, styles["small"]),
                    Paragraph(f"<b>{_pdf_safe(_cell(value))}</b>", styles["h3"]),
                ]
            )
        while len(cells) < 4:
            cells.append("")
        rows.append(cells)

    table = Table(rows, colWidths=[width / 4] * 4, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#cfd8e6")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dfe5ee")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _chart_png(rows: list[dict[str, Any]], title: str, x_key: str, y_key: str, kind: str) -> BytesIO:
    fig = Figure(figsize=(7.1, 3.3), dpi=150, facecolor="white")
    ax = fig.add_subplot(111)

    if kind == "line":
        ordered = sorted(rows, key=lambda row: row.get(x_key) or 0)
        x_values = [row.get(x_key) for row in ordered]
        y_values = [row.get(y_key) or 0 for row in ordered]
        ax.plot(x_values, y_values, color="#2f6f9f", marker="o", linewidth=2, markersize=4)
        ax.set_xlabel("Year")
        ax.set_ylabel("Patent publications")
    else:
        ranked = sorted(rows, key=lambda row: row.get(y_key) or 0, reverse=True)[:12]
        labels = [_truncate(_cell(row.get(x_key)), 34) for row in ranked]
        values = [row.get(y_key) or 0 for row in ranked]
        labels.reverse()
        values.reverse()
        ax.barh(labels, values, color="#2f756d")
        ax.set_xlabel(y_key.replace("_", " ").title())
        ax.tick_params(axis="y", labelsize=7)

    ax.set_title(title, fontsize=10, fontweight="bold", loc="left")
    ax.grid(axis="x" if kind != "line" else "y", color="#d8dee8", linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    png = BytesIO()
    FigureCanvasAgg(fig).print_png(png)
    png.seek(0)
    return png


def _chart_flowables(report: PatentLandscapeReport, styles: dict[str, ParagraphStyle], width: float) -> list[Any]:
    flowables: list[Any] = []
    for title, query_name, x_key, y_key, kind in CHART_SPECS:
        rows = report.query_results.get(query_name, [])
        if not rows:
            continue
        png = _chart_png(rows, title, x_key, y_key, kind)
        flowables.append(
            KeepTogether(
                [
                    _paragraph(title, styles["h3"]),
                    Image(png, width=width, height=3.05 * inch, kind="proportional"),
                    Spacer(1, 8),
                ]
            )
        )
    return flowables


def _table_flowable(table: ReportTable, styles: dict[str, ParagraphStyle], width: float, max_rows: int = 50) -> list[Any]:
    if not table.rows:
        return []
    columns = table.columns
    if not columns:
        return []

    data = [[_paragraph(column.replace("_", " ").title(), styles["table_header"]) for column in columns]]
    for row in table.rows[:max_rows]:
        data.append([_paragraph(_truncate(_cell(row.get(column, ""))), styles["table_cell"]) for column in columns])

    col_width = width / len(columns)
    report_table = Table(data, colWidths=[col_width] * len(columns), repeatRows=1, hAlign="LEFT")
    report_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#bcc7d6")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d9e0ea")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf2f7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    flowables: list[Any] = [_paragraph(table.title, styles["h3"]), report_table, Spacer(1, 8)]
    if len(table.rows) > max_rows:
        flowables.append(_paragraph(f"Table truncated to first {max_rows} rows for PDF readability.", styles["meta"]))
    return flowables


def _key_value_table(title: str, items: dict[str, Any], styles: dict[str, ParagraphStyle], width: float) -> list[Any]:
    if not items:
        return []
    rows = [[_paragraph("Field", styles["table_header"]), _paragraph("Value", styles["table_header"])]]
    rows.extend([[_paragraph(str(key), styles["table_cell"]), _paragraph(_cell(value), styles["table_cell"])] for key, value in items.items()])
    table = Table(rows, colWidths=[width * 0.28, width * 0.72], repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#bcc7d6")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d9e0ea")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf2f7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [_paragraph(title, styles["h2"]), table, Spacer(1, 8)]


def _draw_watermark(canvas: Any, doc: SimpleDocTemplate) -> None:
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#d8dee8"))
    if hasattr(canvas, "setFillAlpha"):
        canvas.setFillAlpha(0.22)
    canvas.setFont("Helvetica-Bold", 20)
    canvas.translate(letter[0] / 2, letter[1] / 2)
    canvas.rotate(35)
    canvas.drawCentredString(0, 0, _pdf_safe(PDF_WATERMARK_TEXT))
    canvas.restoreState()

    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#7b8794"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(letter[0] / 2, 0.24 * inch, _pdf_safe(PDF_WATERMARK_TEXT))
    canvas.restoreState()


def report_to_pdf(report: PatentLandscapeReport) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.45 * inch,
        rightMargin=0.45 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        pageCompression=0,
        title=_pdf_safe(report.title),
    )
    styles = _styles()
    story: list[Any] = [
        _paragraph(report.title, styles["title"]),
        _paragraph(
            f"Report type: {report.report_type} | Input: {report.input_value} | Generated: {report.generated_at}",
            styles["meta"],
        ),
        _paragraph(SOURCE_NOTE, styles["meta"]),
    ]

    metrics = _metric_table(report, styles, doc.width)
    if metrics is not None:
        story.extend([metrics, Spacer(1, 10)])

    charts = _chart_flowables(report, styles, doc.width)
    if charts:
        story.append(_paragraph("Charts", styles["h2"]))
        story.extend(charts)

    for section in report.sections:
        story.append(_paragraph(section.title, styles["h2"]))
        if section.body:
            story.append(_paragraph(section.body, styles["body"]))
        for table in section.tables:
            story.extend(_table_flowable(table, styles, doc.width))

    story.extend(_key_value_table("Data Provenance", report.provenance, styles, doc.width))
    story.extend(_key_value_table("Query Row Counts", report.query_row_counts, styles, doc.width))

    doc.build(story, onFirstPage=_draw_watermark, onLaterPages=_draw_watermark)
    return buffer.getvalue()
