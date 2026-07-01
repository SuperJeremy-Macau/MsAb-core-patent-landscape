from __future__ import annotations

from .common import QueryDefinition


CANCER_EXPRESSION_MATCH = """
MATCH (cancer:Cancer {name: $value})-[:DIFFERENTIAL_AND_HIGHLY_EXPRESSED_IN]-(t:Target)-[:HAS_TARGET]-(tp:TargetPair)-[:HAS_TARGET_PAIR]-(p:Patent)-[:PUBLISHED_IN]-(y:Year)
"""


def cancer_expression_queries() -> list[QueryDefinition]:
    return [
        QueryDefinition(
            name="summary",
            description="Core patent and family counts for a cancer-expression target context.",
            default_limit=1,
            cypher=CANCER_EXPRESSION_MATCH
            + """
OPTIONAL MATCH (p)-[:HAS_PATENT]-(fam:Family)
OPTIONAL MATCH (p)-[:HAS_ASSIGNEE]-(a:Assignee)
WITH p, fam, tp, t, a, toInteger(y.year) AS year_value
WHERE year_value >= $year_min AND year_value <= $year_max
RETURN count(DISTINCT p) AS patent_count,
       count(DISTINCT fam) AS family_count,
       count(DISTINCT tp) AS target_pair_count,
       count(DISTINCT t) AS target_count,
       count(DISTINCT a) AS assignee_count,
       min(year_value) AS first_year,
       max(year_value) AS latest_year
LIMIT 1
""",
        ),
        QueryDefinition(
            name="yearly_trend",
            description="Yearly publication counts for a cancer-expression target context.",
            default_limit=100,
            cypher=CANCER_EXPRESSION_MATCH
            + """
WITH p, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN year, count(DISTINCT p) AS patent_count
ORDER BY year
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="top_targets",
            description="Top targets linked to a cancer-expression context.",
            default_limit=20,
            cypher=CANCER_EXPRESSION_MATCH
            + """
MATCH (p)-[:HAS_PATENT]-(fam:Family)
WITH t, p, fam, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN t.symbol AS target,
       count(DISTINCT p) AS patent_count,
       count(DISTINCT fam) AS family_count
ORDER BY patent_count DESC, family_count DESC, target
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="top_target_pairs",
            description="Top target pairs linked to a cancer-expression context.",
            default_limit=20,
            cypher=CANCER_EXPRESSION_MATCH
            + """
MATCH (p)-[:HAS_PATENT]-(fam:Family)
WITH tp, p, fam, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN tp.name AS target_pair,
       count(DISTINCT p) AS patent_count,
       count(DISTINCT fam) AS family_count
ORDER BY patent_count DESC, family_count DESC, target_pair
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="top_assignees",
            description="Top assignees linked to a cancer-expression context.",
            default_limit=20,
            cypher=CANCER_EXPRESSION_MATCH
            + """
MATCH (p)-[:HAS_ASSIGNEE]-(a:Assignee)
MATCH (p)-[:HAS_PATENT]-(fam:Family)
WITH a, p, fam, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN a.name AS assignee,
       count(DISTINCT p) AS patent_count,
       count(DISTINCT fam) AS family_count
ORDER BY patent_count DESC, family_count DESC, assignee
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="related_pathways",
            description="Pathways represented by targets linked to a cancer-expression context.",
            default_limit=50,
            cypher=CANCER_EXPRESSION_MATCH
            + """
MATCH (t)-[:IN_PATHWAY]-(pathway:Pathway)
WITH pathway, p, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN pathway.name AS pathway,
       count(DISTINCT p) AS patent_count
ORDER BY patent_count DESC, pathway
LIMIT $limit
""",
        ),
        QueryDefinition(
            name="representative_patents",
            description="Representative patent publications for a cancer-expression target context.",
            default_limit=50,
            cypher=CANCER_EXPRESSION_MATCH
            + """
OPTIONAL MATCH (p)-[:HAS_ASSIGNEE]-(a:Assignee)
OPTIONAL MATCH (p)-[:HAS_PATENT]-(fam:Family)
WITH p, tp, t, a, fam, toInteger(y.year) AS year
WHERE year >= $year_min AND year <= $year_max
RETURN p.pub_no AS pub_no,
       year,
       t.symbol AS target,
       tp.name AS target_pair,
       a.name AS assignee,
       fam.family_member AS family_member
ORDER BY year DESC, pub_no
LIMIT $limit
""",
        ),
    ]
