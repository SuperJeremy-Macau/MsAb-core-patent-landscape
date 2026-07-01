from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import PatentLandscapeReport, ReportSection, ReportTable
from .narrative import caveats, evidence_summary, executive_summary, trend_summary


SECTION_TABLES = {
    "Competitive Landscape": ["top_assignees", "origins"],
    "Target or Target-Pair Landscape": ["top_target_pairs", "top_targets"],
    "Biological and Technical Annotations": [
        "annotations",
        "technology_classes",
        "related_functional_roles",
        "related_pathways",
    ],
    "Representative Patent Families and Publications": ["representative_patents"],
}


def _table(title: str, rows: list[dict[str, Any]]) -> ReportTable | None:
    if not rows:
        return None
    return ReportTable(title=title.replace("_", " ").title(), rows=rows)


def _tables_for(section_title: str, results: dict[str, list[dict[str, Any]]]) -> list[ReportTable]:
    tables: list[ReportTable] = []
    for query_name in SECTION_TABLES.get(section_title, []):
        table = _table(query_name, results.get(query_name, []))
        if table is not None:
            tables.append(table)
    return tables


def assemble_report(
    report_type: str,
    value: str,
    results: dict[str, list[dict[str, Any]]],
    provenance: dict[str, Any],
) -> PatentLandscapeReport:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    title = f"{report_type} Patent Landscape: {value}"
    query_row_counts = {name: len(rows) for name, rows in results.items()}

    sections = [
        ReportSection(
            title="Executive Summary",
            body=executive_summary(report_type, value, results.get("summary", [])),
        ),
        ReportSection(
            title="Dataset Scope and Input",
            body=f"Report type: `{report_type}`. Input value: `{value}`. The report is assembled from fixed Cypher templates.",
        ),
        ReportSection(
            title="Publication Trend",
            body=trend_summary(results.get("yearly_trend", [])),
            tables=[table for table in [_table("yearly_trend", results.get("yearly_trend", []))] if table],
        ),
        ReportSection(
            title="Competitive Landscape",
            body="Assignee and origin views summarize the competitive context where data are available.",
            tables=_tables_for("Competitive Landscape", results),
        ),
        ReportSection(
            title="Target or Target-Pair Landscape",
            body="Target and target-pair rankings summarize the main biological combinations represented in the selected report.",
            tables=_tables_for("Target or Target-Pair Landscape", results),
        ),
        ReportSection(
            title="Biological and Technical Annotations",
            body="Annotation tables report pathway, function, cancer, and technology-class context where present in the graph.",
            tables=_tables_for("Biological and Technical Annotations", results),
        ),
        ReportSection(
            title="Representative Patent Families and Publications",
            body=evidence_summary(results.get("representative_patents", [])),
            tables=_tables_for("Representative Patent Families and Publications", results),
        ),
        ReportSection(
            title="Data Provenance",
            body="Query provenance and row counts are recorded with the report so claims can be traced to graph queries.",
        ),
        ReportSection(title="Caveats", body=caveats(results, report_type)),
    ]

    return PatentLandscapeReport(
        report_type=report_type,
        input_value=value,
        title=title,
        generated_at=generated_at,
        sections=sections,
        provenance=provenance,
        query_row_counts=query_row_counts,
        query_results=results,
    )
