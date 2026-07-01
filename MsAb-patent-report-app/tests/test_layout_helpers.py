from msab_patent_report.ui.layout import query_row_count_items, snapshot_metric_items, summary_metric_items


def test_summary_metric_items_prefers_known_count_fields():
    rows = [{"patent_count": 10, "family_count": 3, "first_year": 2018, "latest_year": 2026}]

    metrics = summary_metric_items(rows)

    assert metrics == [
        ("Patent publications", "10"),
        ("Patent families", "3"),
        ("First year", "2018"),
        ("Latest year", "2026"),
    ]


def test_summary_metric_items_includes_assignee_count_when_available():
    rows = [{"patent_count": 10, "family_count": 3, "assignee_count": 5}]

    metrics = summary_metric_items(rows)

    assert ("Assignees", "5") in metrics


def test_snapshot_metric_items_uses_console_order_and_labels():
    snapshot = {
        "patent_count": 20347,
        "family_count": 1850,
        "target_pair_count": 948,
        "target_count": 462,
        "assignee_count": 870,
        "functional_role_count": 47,
    }

    metrics = snapshot_metric_items(snapshot)

    assert metrics == [
        ("Patents", "20,347"),
        ("Families", "1,850"),
        ("Target pairs", "948"),
        ("Targets", "462"),
        ("Assignees", "870"),
        ("Functional roles", "47"),
    ]


def test_query_row_count_items_formats_report_provenance_counts():
    counts = {"summary": 1, "yearly_trend": 17, "representative_patents": 50}

    assert query_row_count_items(counts) == [
        ("summary", "1 row"),
        ("yearly_trend", "17 rows"),
        ("representative_patents", "50 rows"),
    ]
