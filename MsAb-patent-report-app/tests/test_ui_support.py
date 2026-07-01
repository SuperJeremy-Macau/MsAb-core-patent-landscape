from msab_patent_report.db.schema import fetch_database_snapshot, fetch_suggestions, fetch_year_range
from msab_patent_report.report.generator import generate_report, report_queries
from msab_patent_report.ui.charts import bar_chart, yearly_trend_chart
from msab_patent_report.ui.report_options import (
    DEFAULT_VALUES,
    REPORT_LENSES,
    REPORT_TYPE_LABELS,
    all_report_types,
    lens_for_report_type,
)


class FakeRunner:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def run(self, cypher, params=None, enforce_limit=True):
        self.calls.append({"cypher": cypher, "params": params or {}, "enforce_limit": enforce_limit})
        for key, rows in self.responses.items():
            if key in cypher:
                return rows
        return []


def test_fetch_year_range_returns_database_bounds():
    runner = FakeRunner({"min_year": [{"min_year": 1987, "max_year": 2026}]})

    assert fetch_year_range(runner) == (1987, 2026)


def test_fetch_suggestions_returns_values_for_report_type():
    runner = FakeRunner({"TargetPair": [{"value": "BCMA/CD3"}, {"value": "CD20/CD3"}]})

    assert fetch_suggestions(runner, "TargetPair") == ["BCMA/CD3", "CD20/CD3"]


def test_fetch_suggestions_supports_curated_knowledge_lenses():
    cases = {
        "Functional Role": ("Functional_1", [{"value": "T-cell engager"}]),
        "Technology Class": ("TechnologyClass1", [{"value": "Immune cell engager"}]),
        "Pathway": ("Pathway", [{"value": "EGFR signaling pathway"}]),
        "Cancer Expression": ("Cancer", [{"value": "Lung cancer"}]),
    }

    for report_type, (cypher_key, rows) in cases.items():
        runner = FakeRunner({cypher_key: rows})
        assert fetch_suggestions(runner, report_type) == [rows[0]["value"]]
        assert runner.calls[0]["params"]["limit"] == 200


def test_fetch_database_snapshot_includes_curated_knowledge_counts():
    snapshot = {
        "patent_count": 20347,
        "family_count": 1850,
        "target_pair_count": 948,
        "target_count": 462,
        "assignee_count": 870,
        "pathway_count": 1157,
        "cancer_count": 33,
        "technology_class_count": 14,
        "functional_role_count": 21,
    }
    runner = FakeRunner({"functional_role_count": [snapshot]})

    assert fetch_database_snapshot(runner) == snapshot


def test_fetch_database_snapshot_avoids_implicit_grouping_expression():
    runner = FakeRunner({"functional_role_count": [{"functional_role_count": 21}]})

    fetch_database_snapshot(runner)

    cypher = runner.calls[0]["cypher"]
    assert "count(f3) AS functional_3_count" in cypher
    assert "functional_1_count + functional_2_count + functional_3_count AS functional_role_count" in cypher
    assert "functional_1_count + functional_2_count + count(f3)" not in cypher


def test_report_lens_options_group_entity_and_curated_knowledge_reports():
    assert list(REPORT_LENSES) == ["Entity Lens", "Curated Knowledge Lens"]
    assert REPORT_LENSES["Entity Lens"] == ["Target", "TargetPair", "Company"]
    assert REPORT_LENSES["Curated Knowledge Lens"] == [
        "Functional Role",
        "Technology Class",
        "Pathway",
        "Cancer Expression",
    ]
    assert all_report_types() == [
        "Target",
        "TargetPair",
        "Company",
        "Functional Role",
        "Technology Class",
        "Pathway",
        "Cancer Expression",
    ]


def test_report_type_labels_defaults_and_reverse_lens_lookup():
    assert REPORT_TYPE_LABELS["Company"] == "Company / Assignee"
    assert REPORT_TYPE_LABELS["Cancer Expression"] == "Cancer Expression"
    assert DEFAULT_VALUES["Functional Role"] == "Oncology_Effector_Cell_Redirection"
    assert DEFAULT_VALUES["Technology Class"] == "Trans-Bridging Immune Engagers"
    assert DEFAULT_VALUES["Pathway"] == "Adaptive Immune System"
    assert DEFAULT_VALUES["Cancer Expression"] == "Glioblastoma Multiforme"
    assert lens_for_report_type("Pathway") == "Curated Knowledge Lens"
    assert lens_for_report_type("TargetPair") == "Entity Lens"


def test_report_queries_rejects_unknown_type():
    try:
        report_queries("Unknown")
    except ValueError as exc:
        assert "Unsupported report type" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_generate_report_uses_runner_rows():
    runner = FakeRunner(
        {
            "count(DISTINCT p) AS patent_count": [
                {"patent_count": 10, "family_count": 3, "first_year": 2018, "latest_year": 2026}
            ],
            "count(DISTINCT p) AS patent_count\nORDER BY year": [{"year": 2026, "patent_count": 4}],
        }
    )

    report = generate_report(
        runner=runner,
        report_type="TargetPair",
        value="BCMA/CD3",
        year_min=1987,
        year_max=2026,
        provenance={"database": "neo4j"},
    )

    assert report.title == "TargetPair Patent Landscape: BCMA/CD3"
    assert "summary" in report.query_row_counts
    assert runner.calls[0]["params"]["value"] == "BCMA/CD3"


def test_chart_helpers_return_plotly_figures():
    trend = yearly_trend_chart([{"year": 2025, "patent_count": 4}], "Trend")
    bars = bar_chart([{"target_pair": "BCMA/CD3", "patent_count": 4}], "target_pair", "patent_count", "Pairs")

    assert trend.layout.title.text == "Trend"
    assert bars.layout.title.text == "Pairs"
