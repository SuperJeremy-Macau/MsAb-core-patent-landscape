from msab_patent_report.exporters.html import report_to_html
from msab_patent_report.exporters.markdown import report_to_markdown
from msab_patent_report.report.models import PatentLandscapeReport, ReportSection, ReportTable


def make_report():
    return PatentLandscapeReport(
        report_type="Target",
        input_value="CD3",
        title="Target Patent Landscape: CD3",
        generated_at="2026-06-21T20:00:00+00:00",
        sections=[
            ReportSection(
                title="Executive Summary",
                body="CD3 has 10 patents.",
                tables=[ReportTable(title="Summary", rows=[{"patent_count": 10, "family_count": 3}])],
            )
        ],
        provenance={"database": "neo4j"},
        query_row_counts={"summary": 1},
    )


def test_markdown_export_contains_title_table_and_provenance():
    text = report_to_markdown(make_report())
    assert "# Target Patent Landscape: CD3" in text
    assert "| patent_count | family_count |" in text
    assert "Data Provenance" in text


def test_html_export_contains_title_table_and_provenance():
    html = report_to_html(make_report())
    assert "<h1>Target Patent Landscape: CD3</h1>" in html
    assert "<th>patent_count</th>" in html
    assert "Data Provenance" in html
