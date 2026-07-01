from __future__ import annotations

from .common import QueryDefinition


def target_queries() -> list[QueryDefinition]:
    return [
        QueryDefinition(
            name="summary",
            description="Core patent and family counts for a target.",
            default_limit=1,
            cypher="""
MATCH (t:Target {symbol: $value})-[:HAS_TARGET]-(tp:TargetPair)-[:HAS_TARGET_PAIR]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
MATCH (p)-[:HAS_PATENT]-(f:Family)
WITH p, f, toInteger(y.year) AS year_value
WHERE year_value >= $year_min AND year_value <= $year_max
RETURN count(DISTINCT p) AS patent_count,
       count(DISTINCT f) AS family_count,
       min(year_value) AS first_year,
       max(year_value) AS latest_year
LIMIT 1
""",
        ),
        QueryDefinition(
            name="yearly_trend",
            description="Yearly patent publication counts for a target.",
            default_limit=100,
            cypher="""
MATCH (t:Target {symbol: $value})-[:HAS_TARGET]-(tp:TargetPair)-[:HAS_TARGET_PAIR]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
WITH p, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN year, count(DISTINCT p) AS patent_count
ORDER BY year
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="top_target_pairs",
            description="Top target pairs containing the target.",
            default_limit=20,
            cypher="""
MATCH (t:Target {symbol: $value})-[:HAS_TARGET]-(tp:TargetPair)-[:HAS_TARGET_PAIR]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
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
            name="top_assignees",
            description="Top assignees for patents connected to a target.",
            default_limit=20,
            cypher="""
MATCH (t:Target {symbol: $value})-[:HAS_TARGET]-(tp:TargetPair)-[:HAS_TARGET_PAIR]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
MATCH (p)-[:HAS_ASSIGNEE]-(a:Assignee)
MATCH (p)-[:HAS_PATENT]-(f:Family)
WITH a, p, f, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN a.name AS assignee,
       count(DISTINCT p) AS patent_count,
       count(DISTINCT f) AS family_count
ORDER BY patent_count DESC, family_count DESC, assignee
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="annotations",
            description="Target-level pathway, function, cancer, and technology annotations.",
            default_limit=100,
            cypher="""
MATCH (t:Target {symbol: $value})-[:HAS_TARGET]-(tp:TargetPair)-[:HAS_TARGET_PAIR]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
OPTIONAL MATCH (t)-[:IN_PATHWAY]-(pathway:Pathway)
OPTIONAL MATCH (t)-[:DIFFERENTIAL_AND_HIGHLY_EXPRESSED_IN]-(cancer:Cancer)
OPTIONAL MATCH (t)-[:FUNCTIONED_AS_1]-(f1:Functional_1)
OPTIONAL MATCH (t)-[:FUNCTIONED_AS_2]-(f2:Functional_2)
OPTIONAL MATCH (t)-[:FUNCTIONED_AS_3]-(f3:Functional_3)
OPTIONAL MATCH (tp)-[:HAS_TECHNOLOGY_CLASS1]-(tc:TechnologyClass1)
WITH pathway, cancer, f1, f2, f3, tc, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN collect(DISTINCT pathway.name) AS pathways,
       collect(DISTINCT cancer.name) AS cancers,
       collect(DISTINCT f1.name) AS functional_1,
       collect(DISTINCT f2.name) AS functional_2,
       collect(DISTINCT f3.name) AS functional_3,
       collect(DISTINCT tc.name) AS technology_classes
LIMIT 1
""",
        ),
        QueryDefinition(
            name="representative_patents",
            description="Representative patent publications for a target.",
            default_limit=50,
            cypher="""
MATCH (t:Target {symbol: $value})-[:HAS_TARGET]-(tp:TargetPair)-[:HAS_TARGET_PAIR]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
OPTIONAL MATCH (p)-[:HAS_ASSIGNEE]-(a:Assignee)
OPTIONAL MATCH (p)-[:HAS_PATENT]-(f:Family)
WITH p, tp, a, f, toInteger(y.year) AS year
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
