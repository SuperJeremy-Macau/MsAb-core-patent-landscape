from __future__ import annotations

from typing import Any


def _value(row: dict[str, Any], key: str, default: Any = 0) -> Any:
    value = row.get(key, default)
    return default if value is None else value


def executive_summary(report_type: str, value: str, summary_rows: list[dict[str, Any]]) -> str:
    if not summary_rows:
        return f"No summary rows were returned for {report_type} `{value}`."

    row = summary_rows[0]
    patent_count = _value(row, "patent_count")
    family_count = _value(row, "family_count")
    first_year = _value(row, "first_year", "not available")
    latest_year = _value(row, "latest_year", "not available")

    extra = []
    if "target_pair_count" in row:
        extra.append(f"{_value(row, 'target_pair_count')} target pairs")
    if "target_count" in row:
        extra.append(f"{_value(row, 'target_count')} targets")
    if "assignee_count" in row:
        extra.append(f"{_value(row, 'assignee_count')} assignees")
    extra_text = f", including {', '.join(extra)}" if extra else ""

    return (
        f"The {report_type} report for `{value}` covers {patent_count} patent publications "
        f"and {family_count} patent families from {first_year} to {latest_year}{extra_text}."
    )


def trend_summary(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No yearly trend rows were returned for the selected input and year range."
    latest = max(rows, key=lambda row: row.get("year") or 0)
    peak = max(rows, key=lambda row: row.get("patent_count") or 0)
    return (
        f"The latest year represented in the trend is {latest.get('year')}, "
        f"and the peak observed year is {peak.get('year')} with {peak.get('patent_count')} patent publications."
    )


def evidence_summary(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No representative patent publication rows were returned."
    return f"The evidence table lists {len(rows)} representative patent publication rows for review."


def caveats(results: dict[str, list[dict[str, Any]]], report_type: str | None = None) -> str:
    notes = [
        "Counts are based on the current Neo4j snapshot and the selected year range.",
        "Patent-family and publication-level counts answer different questions and should not be treated as interchangeable.",
    ]
    if report_type in {"Functional Role", "Pathway", "Cancer Expression"}:
        notes.append(
            "This report starts from target-level curated knowledge annotations; counts indicate patents connected through annotated targets or target pairs, not standalone patent claims for the annotation."
        )
    if report_type == "Technology Class":
        notes.append(
            "Technology-class reports start from target-pair-level TechnologyClass1 annotations and should not be treated as a complete technology ontology."
        )
    if report_type == "Cancer Expression":
        notes.append(
            "Cancer Expression reports use target expression context and are not patent indication or clinical-use evidence."
        )
    if not results.get("summary"):
        notes.append("No summary rows were returned for the selected input.")
    empty_queries = sorted(name for name, rows in results.items() if not rows)
    if empty_queries:
        notes.append("Empty result sections: " + ", ".join(empty_queries) + ".")
    return "\n".join(f"- {note}" for note in notes)
