from __future__ import annotations

from typing import Any


def fetch_year_range(runner: Any) -> tuple[int, int]:
    rows = runner.run(
        """
MATCH (y:Year)
RETURN min(toInteger(y.year)) AS min_year, max(toInteger(y.year)) AS max_year
""",
        enforce_limit=True,
    )
    if not rows:
        return (1987, 2026)
    row = rows[0]
    return (int(row.get("min_year") or 1987), int(row.get("max_year") or 2026))


def fetch_suggestions(runner: Any, report_type: str, limit: int = 200) -> list[str]:
    queries = {
        "Target": """
MATCH (t:Target)
RETURN t.symbol AS value
ORDER BY value
LIMIT $limit
""",
        "TargetPair": """
MATCH (tp:TargetPair)
RETURN tp.name AS value
ORDER BY value
LIMIT $limit
""",
        "Company": """
MATCH (a:Assignee)
RETURN a.name AS value
ORDER BY value
LIMIT $limit
""",
        "Functional Role": """
MATCH (f1:Functional_1)
RETURN f1.name AS value
UNION
MATCH (f2:Functional_2)
RETURN f2.name AS value
UNION
MATCH (f3:Functional_3)
RETURN f3.name AS value
ORDER BY value
LIMIT $limit
""",
        "Technology Class": """
MATCH (tc:TechnologyClass1)
RETURN tc.name AS value
ORDER BY value
LIMIT $limit
""",
        "Pathway": """
MATCH (pathway:Pathway)
RETURN pathway.name AS value
ORDER BY value
LIMIT $limit
""",
        "Cancer Expression": """
MATCH (cancer:Cancer)
RETURN cancer.name AS value
ORDER BY value
LIMIT $limit
""",
    }
    if report_type not in queries:
        raise ValueError(f"Unsupported report type: {report_type}")
    rows = runner.run(queries[report_type], {"limit": int(limit)})
    return [str(row["value"]) for row in rows if row.get("value")]


def fetch_database_snapshot(runner: Any) -> dict[str, int | str]:
    rows = runner.run(
        """
MATCH (p:Patent)
WITH count(p) AS patent_count
MATCH (f:Family)
WITH patent_count, count(f) AS family_count
MATCH (tp:TargetPair)
WITH patent_count, family_count, count(tp) AS target_pair_count
MATCH (t:Target)
WITH patent_count, family_count, target_pair_count, count(t) AS target_count
MATCH (a:Assignee)
WITH patent_count, family_count, target_pair_count, target_count, count(a) AS assignee_count
MATCH (pathway:Pathway)
WITH patent_count, family_count, target_pair_count, target_count, assignee_count, count(pathway) AS pathway_count
MATCH (cancer:Cancer)
WITH patent_count, family_count, target_pair_count, target_count, assignee_count, pathway_count, count(cancer) AS cancer_count
MATCH (tc:TechnologyClass1)
WITH patent_count, family_count, target_pair_count, target_count, assignee_count, pathway_count, cancer_count, count(tc) AS technology_class_count
MATCH (f1:Functional_1)
WITH patent_count, family_count, target_pair_count, target_count, assignee_count, pathway_count, cancer_count, technology_class_count, count(f1) AS functional_1_count
MATCH (f2:Functional_2)
WITH patent_count, family_count, target_pair_count, target_count, assignee_count, pathway_count, cancer_count, technology_class_count, functional_1_count, count(f2) AS functional_2_count
MATCH (f3:Functional_3)
WITH patent_count,
     family_count,
     target_pair_count,
     target_count,
     assignee_count,
     pathway_count,
     cancer_count,
     technology_class_count,
     functional_1_count,
     functional_2_count,
     count(f3) AS functional_3_count
RETURN patent_count,
       family_count,
       target_pair_count,
       target_count,
       assignee_count,
       pathway_count,
       cancer_count,
       technology_class_count,
       functional_1_count + functional_2_count + functional_3_count AS functional_role_count
""",
        enforce_limit=True,
    )
    if not rows:
        return {}
    return rows[0]
