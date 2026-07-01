from msab_patent_report.report.assembler import assemble_report


def test_assemble_report_contains_required_sections():
    results = {
        "summary": [{"patent_count": 10, "family_count": 3, "first_year": 2018, "latest_year": 2026}],
        "yearly_trend": [{"year": 2025, "patent_count": 4}],
        "representative_patents": [
            {"pub_no": "WO2025000001", "year": 2025, "assignee": "Example", "target_pair": "BCMA/CD3"}
        ],
    }

    report = assemble_report("TargetPair", "BCMA/CD3", results, {"database": "neo4j"})

    assert report.title == "TargetPair Patent Landscape: BCMA/CD3"
    assert "Executive Summary" in [section.title for section in report.sections]
    assert "Representative Patent Families and Publications" in [section.title for section in report.sections]
    assert report.provenance["database"] == "neo4j"
    assert report.query_row_counts["summary"] == 1


def test_assemble_report_keeps_empty_query_results_as_caveats():
    report = assemble_report("Company", "Unknown", {"summary": []}, {"database": "neo4j"})

    caveat_section = next(section for section in report.sections if section.title == "Caveats")
    assert "No summary rows were returned" in caveat_section.body


def test_cancer_expression_report_caveat_distinguishes_expression_from_indication():
    report = assemble_report(
        "Cancer Expression",
        "Lung cancer",
        {
            "summary": [
                {
                    "patent_count": 10,
                    "family_count": 3,
                    "target_count": 2,
                    "target_pair_count": 4,
                    "assignee_count": 5,
                    "first_year": 2018,
                    "latest_year": 2026,
                }
            ]
        },
        {"database": "neo4j"},
    )

    caveat_section = next(section for section in report.sections if section.title == "Caveats")
    assert "expression context" in caveat_section.body
    assert "not patent indication or clinical-use evidence" in caveat_section.body
