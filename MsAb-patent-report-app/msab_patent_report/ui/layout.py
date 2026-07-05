from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from msab_patent_report.exporters.html import report_to_html
from msab_patent_report.exporters.markdown import report_to_markdown
from msab_patent_report.exporters.pdf import report_to_pdf
from msab_patent_report.report.models import PatentLandscapeReport, ReportTable
from msab_patent_report.ui.charts import bar_chart, yearly_trend_chart


METRIC_LABELS = {
    "patent_count": "Patent publications",
    "family_count": "Patent families",
    "target_pair_count": "Target pairs",
    "target_count": "Targets",
    "assignee_count": "Assignees",
    "first_year": "First year",
    "latest_year": "Latest year",
}

SNAPSHOT_LABELS = {
    "patent_count": "Patents",
    "family_count": "Families",
    "target_pair_count": "Target pairs",
    "target_count": "Targets",
    "assignee_count": "Assignees",
    "pathway_count": "Pathways",
    "cancer_count": "Cancer contexts",
    "technology_class_count": "Technology classes",
    "functional_role_count": "Functional roles",
}

SNAPSHOT_ORDER = (
    "patent_count",
    "family_count",
    "target_pair_count",
    "target_count",
    "assignee_count",
    "pathway_count",
    "cancer_count",
    "technology_class_count",
    "functional_role_count",
)


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def summary_metric_items(summary_rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    if not summary_rows:
        return []
    row = summary_rows[0]
    items: list[tuple[str, str]] = []
    for key in (
        "patent_count",
        "family_count",
        "target_pair_count",
        "target_count",
        "assignee_count",
        "first_year",
        "latest_year",
    ):
        value = row.get(key)
        if value is not None:
            items.append((METRIC_LABELS[key], str(value)))
    return items


def snapshot_metric_items(snapshot: dict[str, Any]) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for key in SNAPSHOT_ORDER:
        value = snapshot.get(key)
        if value is not None:
            items.append((SNAPSHOT_LABELS[key], _format_value(value)))
    return items


def query_row_count_items(counts: dict[str, int]) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for name, count in counts.items():
        unit = "row" if count == 1 else "rows"
        items.append((name, f"{count:,} {unit}"))
    return items


def render_metric_cards(items: list[tuple[str, str]], columns_per_row: int = 4) -> None:
    for start in range(0, len(items), columns_per_row):
        row_items = items[start : start + columns_per_row]
        columns = st.columns(len(row_items))
        for column, (label, value) in zip(columns, row_items):
            column.markdown(
                f"""
<div class="msab-metric-card">
  <div class="msab-metric-label">{escape(label)}</div>
  <div class="msab-metric-value">{escape(value)}</div>
</div>
""",
                unsafe_allow_html=True,
            )


def render_app_header(snapshot: dict[str, Any], connected: bool, year_range: tuple[int, int]) -> None:
    status = "Connected" if connected else "Connection unavailable"
    status_color = "#2f756d" if connected else "#c4514a"
    patent_count = snapshot.get("patent_count", "NA")
    family_count = snapshot.get("family_count", "NA")
    year_min, year_max = year_range
    st.markdown(
        f"""
<div class="msab-hero">
  <div class="msab-hero-title">MsAb Patent Report Console</div>
  <div class="msab-hero-subtitle">
    Deterministic, evidence-backed landscape reports from the curated multispecific antibody patent knowledge graph.
  </div>
  <div class="msab-status-row">
    <div class="msab-pill"><strong style="color:{status_color};">{escape(status)}</strong></div>
    <div class="msab-pill">Patents <strong>{escape(_format_value(patent_count))}</strong></div>
    <div class="msab-pill">Families <strong>{escape(_format_value(family_count))}</strong></div>
    <div class="msab-pill">Years <strong>{year_min}-{year_max}</strong></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_panel_heading(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f'<div class="msab-panel-subtitle">{escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
<div>
  <div class="msab-panel-title">{escape(title)}</div>
  {subtitle_html}
</div>
""",
        unsafe_allow_html=True,
    )


def render_snapshot_panel(snapshot: dict[str, Any], connected: bool, error_message: str | None = None) -> None:
    render_panel_heading("Knowledge Graph Snapshot", "Read-only graph context used by report suggestions and provenance.")
    if not connected:
        st.warning("Neo4j snapshot is unavailable.")
        if error_message:
            with st.expander("Connection detail"):
                st.code(error_message)
        return

    items = snapshot_metric_items(snapshot)
    if not items:
        st.caption("Snapshot unavailable.")
        return

    render_metric_cards(items, columns_per_row=2)


def _render_table(table: ReportTable) -> None:
    if not table.rows:
        return
    st.caption(table.title)
    st.dataframe(pd.DataFrame(table.rows), width="stretch", hide_index=True)


def render_report(report: PatentLandscapeReport) -> None:
    st.markdown(f"### {report.title}")
    st.caption(f"Generated at {report.generated_at}. All factual content is assembled from fixed Neo4j query templates.")
    metrics = summary_metric_items(report.query_results.get("summary", []))
    if metrics:
        render_metric_cards(metrics, columns_per_row=4)

    trend_rows = report.query_results.get("yearly_trend", [])
    if trend_rows:
        with st.container(border=True):
            st.plotly_chart(yearly_trend_chart(trend_rows, "Publication trend"), width="stretch")

    chart_columns = st.columns(2)
    if report.query_results.get("top_assignees"):
        with chart_columns[0].container(border=True):
            st.plotly_chart(
                bar_chart(report.query_results["top_assignees"][:15], "assignee", "patent_count", "Top assignees"),
                width="stretch",
            )
    if report.query_results.get("top_target_pairs"):
        with chart_columns[1].container(border=True):
            st.plotly_chart(
                bar_chart(report.query_results["top_target_pairs"][:15], "target_pair", "patent_count", "Top target pairs"),
                width="stretch",
            )
    if report.query_results.get("top_targets"):
        with chart_columns[1].container(border=True):
            st.plotly_chart(
                bar_chart(report.query_results["top_targets"][:15], "target", "patent_count", "Top targets"),
                width="stretch",
            )

    for section in report.sections:
        with st.expander(section.title, expanded=section.title in {"Executive Summary", "Representative Patent Families and Publications"}):
            st.markdown(section.body)
            for table in section.tables:
                _render_table(table)


def render_report_controls(report: PatentLandscapeReport) -> None:
    render_panel_heading("Report Controls", "Evidence, provenance, and export for the generated report.")
    st.caption("Outline")
    for idx, section in enumerate(report.sections, start=1):
        st.write(f"{idx}. {section.title}")

    st.caption("Query rows")
    for name, value in query_row_count_items(report.query_row_counts):
        st.write(f"`{name}`: {value}")

    if report.provenance:
        st.caption("Provenance")
        for key, value in report.provenance.items():
            st.write(f"`{key}`: {value}")

    markdown = report_to_markdown(report)
    html = report_to_html(report)
    pdf = report_to_pdf(report)
    safe_name = report.input_value.replace("/", "-").replace(" ", "_")
    st.download_button(
        "Download Markdown",
        data=markdown,
        file_name=f"{report.report_type}_{safe_name}_patent_landscape.md",
        mime="text/markdown",
        width="stretch",
    )
    st.download_button(
        "Download HTML",
        data=html,
        file_name=f"{report.report_type}_{safe_name}_patent_landscape.html",
        mime="text/html",
        width="stretch",
    )
    st.download_button(
        "Download PDF",
        data=pdf,
        file_name=f"{report.report_type}_{safe_name}_patent_landscape.pdf",
        mime="application/pdf",
        width="stretch",
    )


def render_empty_report_state(snapshot: dict[str, Any], year_range: tuple[int, int]) -> None:
    year_min, year_max = year_range
    st.markdown(
        f"""
<div class="msab-empty">
  <h2>Report canvas</h2>
  <p>Configured for the {year_min}-{year_max} MsAb/BsAb patent graph snapshot. Generated reports will appear here with metrics, charts, evidence tables, provenance, and caveats.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    items = snapshot_metric_items(snapshot)[:6]
    if items:
        st.write("")
        render_metric_cards(items, columns_per_row=3)
