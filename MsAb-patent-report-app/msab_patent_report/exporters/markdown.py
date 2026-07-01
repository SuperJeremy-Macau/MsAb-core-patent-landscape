from __future__ import annotations

from typing import Any
import json

from msab_patent_report.report.models import PatentLandscapeReport, ReportTable


def _cell(value: Any) -> str:
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table_to_markdown(table: ReportTable) -> str:
    if not table.rows:
        return ""
    columns = table.columns
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(_cell(row.get(column, "")) for column in columns) + " |" for row in table.rows]
    return "\n".join([f"### {table.title}", header, separator, *body])


def report_to_markdown(report: PatentLandscapeReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        f"- Report type: `{report.report_type}`",
        f"- Input value: `{report.input_value}`",
        f"- Generated at: `{report.generated_at}`",
        "",
    ]

    for section in report.sections:
        lines.extend([f"## {section.title}", "", section.body, ""])
        for table in section.tables:
            table_text = _table_to_markdown(table)
            if table_text:
                lines.extend([table_text, ""])

    lines.extend(["## Data Provenance", ""])
    for key, value in report.provenance.items():
        lines.append(f"- {key}: `{_cell(value)}`")
    lines.extend(["", "## Query Row Counts", ""])
    for key, value in report.query_row_counts.items():
        lines.append(f"- {key}: {value}")

    return "\n".join(lines).strip() + "\n"
