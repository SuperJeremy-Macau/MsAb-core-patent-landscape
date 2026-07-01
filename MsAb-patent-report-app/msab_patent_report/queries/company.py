from __future__ import annotations

from .common import QueryDefinition


def company_queries() -> list[QueryDefinition]:
    return [
        QueryDefinition(
            name="summary",
            description="Core portfolio counts for an assignee.",
            default_limit=1,
            cypher="""
MATCH (a:Assignee)-[:HAS_ASSIGNEE]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
WHERE toLower(a.name) = toLower($value)
OPTIONAL MATCH (p)-[:HAS_PATENT]-(f:Family)
OPTIONAL MATCH (p)-[:HAS_TARGET_PAIR]-(tp:TargetPair)
OPTIONAL MATCH (tp)-[:HAS_TARGET]-(t:Target)
WITH p, f, tp, t, toInteger(y.year) AS year_value
WHERE year_value >= $year_min AND year_value <= $year_max
RETURN count(DISTINCT p) AS patent_count,
       count(DISTINCT f) AS family_count,
       count(DISTINCT tp) AS target_pair_count,
       count(DISTINCT t) AS target_count,
       min(year_value) AS first_year,
       max(year_value) AS latest_year
LIMIT 1
""",
        ),
        QueryDefinition(
            name="yearly_trend",
            description="Yearly publication counts for an assignee portfolio.",
            default_limit=100,
            cypher="""
MATCH (a:Assignee)-[:HAS_ASSIGNEE]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
WHERE toLower(a.name) = toLower($value)
WITH p, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN year, count(DISTINCT p) AS patent_count
ORDER BY year
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="top_target_pairs",
            description="Top target pairs in an assignee portfolio.",
            default_limit=20,
            cypher="""
MATCH (a:Assignee)-[:HAS_ASSIGNEE]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
WHERE toLower(a.name) = toLower($value)
MATCH (p)-[:HAS_TARGET_PAIR]-(tp:TargetPair)
MATCH (p)-[:HAS_PATENT]-(f:Family)
WITH tp, p, f, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN tp.name AS target_pair,
       count(DISTINCT p) AS patent_count,
       count(DISTINCT f) AS family_count
ORDER BY patent_count DESC, family_count DESC, target_pair
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="top_targets",
            description="Top individual targets in an assignee portfolio.",
            default_limit=20,
            cypher="""
MATCH (a:Assignee)-[:HAS_ASSIGNEE]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
WHERE toLower(a.name) = toLower($value)
MATCH (p)-[:HAS_TARGET_PAIR]-(tp:TargetPair)-[:HAS_TARGET]-(t:Target)
WITH t, p, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN t.symbol AS target,
       count(DISTINCT p) AS patent_count
ORDER BY patent_count DESC, target
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="technology_classes",
            description="Technology class distribution in an assignee portfolio.",
            default_limit=20,
            cypher="""
MATCH (a:Assignee)-[:HAS_ASSIGNEE]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
WHERE toLower(a.name) = toLower($value)
MATCH (p)-[:HAS_TARGET_PAIR]-(tp:TargetPair)-[:HAS_TECHNOLOGY_CLASS1]-(tc:TechnologyClass1)
WITH tc, p, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN tc.name AS technology_class,
       count(DISTINCT p) AS patent_count
ORDER BY patent_count DESC, technology_class
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="annotations",
            description="Pathway and function annotations represented in an assignee portfolio.",
            default_limit=100,
            cypher="""
MATCH (a:Assignee)-[:HAS_ASSIGNEE]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
WHERE toLower(a.name) = toLower($value)
MATCH (p)-[:HAS_TARGET_PAIR]-(tp:TargetPair)-[:HAS_TARGET]-(t:Target)
OPTIONAL MATCH (t)-[:IN_PATHWAY]-(pathway:Pathway)
OPTIONAL MATCH (t)-[:FUNCTIONED_AS_1]-(f1:Functional_1)
OPTIONAL MATCH (t)-[:FUNCTIONED_AS_2]-(f2:Functional_2)
OPTIONAL MATCH (t)-[:FUNCTIONED_AS_3]-(f3:Functional_3)
WITH pathway, f1, f2, f3, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN collect(DISTINCT pathway.name) AS pathways,
       collect(DISTINCT f1.name) AS functional_1,
       collect(DISTINCT f2.name) AS functional_2,
       collect(DISTINCT f3.name) AS functional_3
LIMIT 1
""",
        ),
        QueryDefinition(
            name="representative_patents",
            description="Representative patent publications for an assignee.",
            default_limit=50,
            cypher="""
MATCH (a:Assignee)-[:HAS_ASSIGNEE]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
WHERE toLower(a.name) = toLower($value)
OPTIONAL MATCH (p)-[:HAS_TARGET_PAIR]-(tp:TargetPair)
OPTIONAL MATCH (p)-[:HAS_PATENT]-(f:Family)
WITH p, tp, f, a, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN p.pub_no AS pub_no,
       year,
       tp.name AS target_pair,
       a.name AS assignee,
       f.family_member AS family_member
ORDER BY year DESC, pub_no
LIMIT $limit
""",
        ),
    ]
