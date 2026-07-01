from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings_loader import load_settings
from msab_patent_report.db.neo4j_runner import Neo4jRunner
from msab_patent_report.report.generator import generate_report


CASES = [
    ("Target", "CD3"),
    ("TargetPair", "BCMA/CD3"),
    ("Company", "ROCHE HOLDING LTD."),
    ("Functional Role", "Oncology_Effector_Cell_Redirection"),
    ("Technology Class", "Trans-Bridging Immune Engagers"),
    ("Pathway", "Adaptive Immune System"),
    ("Cancer Expression", "Glioblastoma Multiforme"),
]


def main() -> int:
    cfg = load_settings(PROJECT_ROOT / "config" / "settings.example.yaml")
    neo = cfg["neo4j"]
    runner = Neo4jRunner(
        uri=neo["uri"],
        user=neo["user"],
        password=neo["password"],
        database=neo.get("database", "neo4j"),
        max_rows=int(neo.get("max_rows", 200)),
    )
    try:
        for report_type, value in CASES:
            report = generate_report(
                runner=runner,
                report_type=report_type,
                value=value,
                year_min=int(cfg.get("report", {}).get("default_year_min", 1987)),
                year_max=int(cfg.get("report", {}).get("default_year_max", 2026)),
                provenance={"database": neo.get("database", "neo4j"), "source": "Neo4j knowledge graph"},
            )
            section_titles = {section.title for section in report.sections}
            required = {"Executive Summary", "Representative Patent Families and Publications", "Caveats"}
            status = "PASS" if required.issubset(section_titles) else "FAIL"
            print(f"{status} {report_type} {value}")
            print("  row_counts:", report.query_row_counts)
    finally:
        runner.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
