from __future__ import annotations


REPORT_LENSES = {
    "Entity Lens": ["Target", "TargetPair", "Company"],
    "Curated Knowledge Lens": [
        "Functional Role",
        "Technology Class",
        "Pathway",
        "Cancer Expression",
    ],
}

REPORT_TYPE_LABELS = {
    "Target": "Target",
    "TargetPair": "Target Pair",
    "Company": "Company / Assignee",
    "Functional Role": "Functional Role",
    "Technology Class": "Technology Class",
    "Pathway": "Pathway",
    "Cancer Expression": "Cancer Expression",
}

REPORT_TYPE_DESCRIPTIONS = {
    "Entity Lens": "Start from graph entities such as targets, target pairs, or assignees.",
    "Curated Knowledge Lens": "Start from manually curated biological and technical knowledge layers.",
    "Target": "Landscape centered on one target symbol.",
    "TargetPair": "Landscape centered on one target-pair name.",
    "Company": "Landscape centered on one assignee or parent-company name.",
    "Functional Role": "Landscape centered on a target functional role curated across Functional_1/2/3.",
    "Technology Class": "Landscape centered on a TechnologyClass1 category.",
    "Pathway": "Landscape centered on targets linked to one pathway.",
    "Cancer Expression": "Landscape centered on targets linked to differential or high expression in one cancer context.",
}

DEFAULT_VALUES = {
    "Target": "CD3",
    "TargetPair": "BCMA/CD3",
    "Company": "ROCHE HOLDING LTD.",
    "Functional Role": "Oncology_Effector_Cell_Redirection",
    "Technology Class": "Trans-Bridging Immune Engagers",
    "Pathway": "Adaptive Immune System",
    "Cancer Expression": "Glioblastoma Multiforme",
}


def all_report_types() -> list[str]:
    report_types: list[str] = []
    for group in REPORT_LENSES.values():
        report_types.extend(group)
    return report_types


def lens_for_report_type(report_type: str) -> str:
    for lens, report_types in REPORT_LENSES.items():
        if report_type in report_types:
            return lens
    raise ValueError(f"Unsupported report type: {report_type}")
