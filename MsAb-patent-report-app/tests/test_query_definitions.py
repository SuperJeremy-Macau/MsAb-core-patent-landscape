from msab_patent_report.db.neo4j_runner import assert_read_only_cypher
from msab_patent_report.report.generator import report_queries
from msab_patent_report.queries.company import company_queries
from msab_patent_report.queries.target import target_queries
from msab_patent_report.queries.target_pair import target_pair_queries


ALL_REPORT_TYPES = [
    "Target",
    "TargetPair",
    "Company",
    "Functional Role",
    "Technology Class",
    "Pathway",
    "Cancer Expression",
]


def test_each_report_type_has_required_queries():
    for bundle in (report_queries(report_type) for report_type in ALL_REPORT_TYPES):
        names = {q.name for q in bundle}
        assert "summary" in names
        assert "yearly_trend" in names
        assert "representative_patents" in names
        assert all(q.cypher.strip().startswith("MATCH") for q in bundle)
        assert all("RETURN" in q.cypher for q in bundle)


def test_queries_are_read_only_and_parameterized():
    for bundle in (report_queries(report_type) for report_type in ALL_REPORT_TYPES):
        for query in bundle:
            assert_read_only_cypher(query.cypher)
            assert "$value" in query.cypher
            assert query.default_limit > 0


def test_curated_knowledge_reports_have_context_queries():
    expected = {
        "Functional Role": {"top_targets", "top_target_pairs", "top_assignees", "related_pathways"},
        "Technology Class": {"top_target_pairs", "top_targets", "top_assignees", "related_functional_roles"},
        "Pathway": {"top_targets", "top_target_pairs", "top_assignees", "related_functional_roles"},
        "Cancer Expression": {"top_targets", "top_target_pairs", "top_assignees", "related_pathways"},
    }

    for report_type, required_queries in expected.items():
        names = {q.name for q in report_queries(report_type)}
        assert required_queries.issubset(names)


def test_company_queries_match_assignee_case_insensitively():
    for query in company_queries():
        assert "toLower(a.name) = toLower($value)" in query.cypher
