from __future__ import annotations

from typing import Any

from msab_patent_report.queries.common import QueryDefinition
from msab_patent_report.queries.company import company_queries
from msab_patent_report.queries.cancer_expression import cancer_expression_queries
from msab_patent_report.queries.functional_role import functional_role_queries
from msab_patent_report.queries.pathway import pathway_queries
from msab_patent_report.queries.target import target_queries
from msab_patent_report.queries.target_pair import target_pair_queries
from msab_patent_report.queries.technology_class import technology_class_queries

from .assembler import assemble_report
from .models import PatentLandscapeReport


def report_queries(report_type: str) -> list[QueryDefinition]:
    if report_type == "Target":
        return target_queries()
    if report_type == "TargetPair":
        return target_pair_queries()
    if report_type == "Company":
        return company_queries()
    if report_type == "Functional Role":
        return functional_role_queries()
    if report_type == "Technology Class":
        return technology_class_queries()
    if report_type == "Pathway":
        return pathway_queries()
    if report_type == "Cancer Expression":
        return cancer_expression_queries()
    raise ValueError(f"Unsupported report type: {report_type}")


def generate_report(
    runner: Any,
    report_type: str,
    value: str,
    year_min: int,
    year_max: int,
    provenance: dict[str, Any] | None = None,
) -> PatentLandscapeReport:
    results: dict[str, list[dict[str, Any]]] = {}
    for query in report_queries(report_type):
        params = {
            "value": value,
            "year_min": int(year_min),
            "year_max": int(year_max),
            "limit": int(query.default_limit),
        }
        results[query.name] = runner.run(query.cypher, params=params)

    report_provenance = dict(provenance or {})
    report_provenance.update(
        {
            "report_type": report_type,
            "input_value": value,
            "year_min": int(year_min),
            "year_max": int(year_max),
            "query_names": ", ".join(query.name for query in report_queries(report_type)),
        }
    )
    return assemble_report(report_type, value, results, report_provenance)
