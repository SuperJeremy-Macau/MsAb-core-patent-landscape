from __future__ import annotations

from typing import Any
import html
import json

from msab_patent_report.branding import PROJECT_URL, SOURCE_NOTE
from msab_patent_report.report.models import PatentLandscapeReport, ReportTable


def _cell(value: Any) -> str:
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    return html.escape(str(value))


def _paragraphs(text: str) -> str:
    parts = [part.strip() for part in text.split("\n") if part.strip()]
    return "\n".join(f"<p>{html.escape(part)}</p>" for part in parts)


def _table_to_html(table: ReportTable) -> str:
    if not table.rows:
        return ""
    columns = table.columns
    thead = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    rows = []
    for row in table.rows:
        cells = "".join(f"<td>{_cell(row.get(column, ''))}</td>" for column in columns)
        rows.append(f"<tr>{cells}</tr>")
    return (
        f"<h3>{html.escape(table.title)}</h3>"
        "<div class=\"table-wrap\"><table>"
        f"<thead><tr>{thead}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def report_to_html(report: PatentLandscapeReport) -> str:
    section_html = []
    for section in report.sections:
        tables = "".join(_table_to_html(table) for table in section.tables)
        section_html.append(
            f"<section><h2>{html.escape(section.title)}</h2>{_paragraphs(section.body)}{tables}</section>"
        )

    provenance = "".join(
        f"<li><strong>{html.escape(str(key))}:</strong> {_cell(value)}</li>"
        for key, value in report.provenance.items()
    )
    row_counts = "".join(
        f"<li><strong>{html.escape(str(key))}:</strong> {int(value)}</li>"
        for key, value in report.query_row_counts.items()
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(report.title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; color: #172033; margin: 32px; line-height: 1.55; }}
    h1 {{ font-size: 28px; margin-bottom: 8px; }}
    h2 {{ border-top: 1px solid #d8dee8; padding-top: 18px; margin-top: 24px; }}
    h3 {{ margin-bottom: 8px; }}
    .meta {{ color: #526071; margin-bottom: 24px; }}
    .source-note {{ border: 1px solid #d8dee8; background: #f7fafc; padding: 10px 12px; margin: 12px 0 22px; color: #3e4a5a; }}
    .source-note a {{ color: #2f6f9f; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #d8dee8; padding: 7px 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f6fa; }}
    .table-wrap {{ overflow-x: auto; margin: 10px 0 18px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report.title)}</h1>
  <div class="meta">Report type: {html.escape(report.report_type)} | Input: {html.escape(report.input_value)} | Generated: {html.escape(report.generated_at)}</div>
  <div class="source-note">{html.escape(SOURCE_NOTE)} <a href="{html.escape(PROJECT_URL)}">{html.escape(PROJECT_URL)}</a></div>
  {''.join(section_html)}
  <section><h2>Data Provenance</h2><ul>{provenance}</ul></section>
  <section><h2>Query Row Counts</h2><ul>{row_counts}</ul></section>
  <section><h2>Report Source</h2><p>{html.escape(SOURCE_NOTE)}</p></section>
</body>
</html>
"""
