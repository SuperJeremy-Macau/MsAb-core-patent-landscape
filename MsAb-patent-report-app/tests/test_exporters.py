from msab_patent_report.exporters.html import report_to_html
from msab_patent_report.exporters.markdown import report_to_markdown
from msab_patent_report.exporters.pdf import report_to_pdf
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


def make_rich_report():
    query_results = {
        "summary": [
            {
                "patent_count": 6874,
                "family_count": 517,
                "first_year": 1994,
                "latest_year": 2026,
            }
        ],
        "yearly_trend": [
            {"year": 2022, "patent_count": 521},
            {"year": 2023, "patent_count": 710},
            {"year": 2024, "patent_count": 790},
            {"year": 2025, "patent_count": 866},
        ],
        "top_assignees": [
            {"assignee": "AMGEN INC", "patent_count": 822},
            {"assignee": "REGENERON PHARMACEUTICALS INC.", "patent_count": 644},
        ],
        "top_target_pairs": [
            {"target_pair": "BCMA/CD3", "patent_count": 603},
            {"target_pair": "CD3/EGFR", "patent_count": 412},
        ],
        "representative_patents": [
            {"pub_no": "WO2025000001", "year": 2025, "target_pair": "BCMA/CD3", "assignee": "AMGEN INC"}
        ],
    }
    return PatentLandscapeReport(
        report_type="Target",
        input_value="CD3",
        title="Target Patent Landscape: CD3",
        generated_at="2026-06-21T20:00:00+00:00",
        sections=[
            ReportSection(title="Executive Summary", body="CD3 has a large patent landscape."),
            ReportSection(
                title="Representative Patent Families and Publications",
                body="The evidence table lists representative patent publication rows.",
                tables=[ReportTable(title="Representative Patents", rows=query_results["representative_patents"])],
            ),
            ReportSection(title="Caveats", body="Counts reflect graph curation scope."),
        ],
        provenance={"database": "neo4j", "source": "Neo4j knowledge graph"},
        query_row_counts={name: len(rows) for name, rows in query_results.items()},
        query_results=query_results,
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


def test_pdf_export_returns_pdf_bytes_with_title_table_and_provenance():
    pdf = report_to_pdf(make_report())

    assert pdf.startswith(b"%PDF-")
    assert b"Target Patent Landscape: CD3" in pdf
    assert b"Summary" in pdf
    assert b"database" in pdf


def test_pdf_export_embeds_summary_charts_and_evidence_tables():
    pdf = report_to_pdf(make_rich_report())

    assert b"Patent publications" in pdf
    assert b"Publication trend" in pdf
    assert b"Top assignees" in pdf
    assert b"Representative Patents" in pdf
    assert pdf.count(b"/Subtype /Image") >= 3
