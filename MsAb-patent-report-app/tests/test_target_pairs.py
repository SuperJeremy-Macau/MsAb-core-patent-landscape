from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from msab_patent_report.target_pairs import (
    TargetPairOption as Option, fetch_target_pairs, search_target_pairs,
    validate_target_pair_selection,
)
from msab_patent_report.report.generator import generate_report


OPTIONS = [
    Option("BCMA/CD3", ("BCMA", "CD3")),
    Option("BCMA/CD3/CD28", ("BCMA", "CD3", "CD28")),
    Option("CD30/BCMA", ("CD30", "BCMA")),
    Option("HLA-A*02:01/NY-ESO-1/CD3", ("HLA-A*02:01/NY-ESO-1", "CD3")),
    Option("unlinked/special", ()),
]


@pytest.mark.parametrize("query", ["CD3 BCMA", "BCMA CD3", "CD3/BCMA", " bcma  cd3 ", "BCMA/CD3"])
def test_and_search_order_case_and_format(query):
    assert search_target_pairs(OPTIONS, query) == ["BCMA/CD3", "BCMA/CD3/CD28"]


def test_exact_target_does_not_match_cd30_and_keeps_multitargets():
    assert set(search_target_pairs(OPTIONS, "CD3")) == {OPTIONS[i].name for i in (0, 1, 3)}
    assert "CD30/BCMA" in search_target_pairs(OPTIONS, "cd")
    assert search_target_pairs(OPTIONS, "does-not-exist") == []


def test_compound_target_and_complete_names_are_preserved():
    assert search_target_pairs(OPTIONS, "HLA-A*02:01/NY-ESO-1 CD3") == [OPTIONS[3].name]
    assert search_target_pairs(OPTIONS, OPTIONS[3].name) == [OPTIONS[3].name]
    assert search_target_pairs(OPTIONS, "unlinked/special") == ["unlinked/special"]


def test_ambiguous_slash_keeps_both_possible_memberships():
    options = [Option("compound+C", ("A/B", "C")), Option("triple", ("A", "B", "C"))]
    assert set(search_target_pairs(options, "A/B C")) == {"compound+C", "triple"}


def test_complete_catalogue_bypasses_default_limit_and_merges_names():
    runner = Mock()
    runner.run.return_value = [
        {"name": f"pair-{i:04}", "targets": ["CD3"]} for i in reversed(range(1200))
    ] + [{"name": "pair-0000", "targets": ["BCMA"]}, {"name": " ", "targets": []}]
    options = fetch_target_pairs(runner)
    assert len(options) == 1200
    assert options[0].targets == ("BCMA", "CD3")
    assert search_target_pairs(options, "pair-1199")[0] == "pair-1199"
    assert search_target_pairs(options, "") == [o.name for o in options]
    assert runner.run.call_args.kwargs["enforce_limit"] is False
    assert "LIMIT" not in runner.run.call_args.args[0]


def test_submission_rejects_free_text_and_stale_database_names():
    with pytest.raises(ValueError, match="Select an existing"):
        validate_target_pair_selection("CD3 BCMA", ["BCMA/CD3"])
    runner = Mock()
    runner.run.return_value = [{"count": 0}]
    with pytest.raises(ValueError, match="Refresh combinations"):
        generate_report(runner, "TargetPair", "deleted-name", 1987, 2026)
    assert runner.run.call_count == 1
    assert runner.run.call_args.args[1] == {"value": "deleted-name"}


UI = '''
import streamlit as st
import app
from unittest.mock import Mock
from msab_patent_report.target_pairs import TargetPairOption
app.cached_year_range = lambda: (1987, 2026)
app.cached_snapshot = lambda: {}
app.cached_suggestions = lambda report_type: ["CD3"]
options = [TargetPairOption("BCMA/CD3", ("BCMA", "CD3")),
           TargetPairOption("BCMA/CD3/CD28", ("BCMA", "CD3", "CD28")),
           TargetPairOption("EGFR/MET", ("EGFR", "MET"))]
catalogue = Mock(return_value=options)
if st.session_state.get("fail_load"):
    catalogue.side_effect = RuntimeError("offline")
app.cached_target_pairs = catalogue
selected, candidates = app.target_pair_input(True)
st.button("Generate Report", disabled=selected not in candidates)
'''


def _pair_ui():
    at = AppTest.from_string(UI).run()
    assert not at.exception
    return at


def _generate(at):
    return next(b for b in at.button if b.label == "Generate Report")


def test_ui_requires_selection_and_clears_invalid_previous_selection():
    at = _pair_ui()
    assert _generate(at).disabled
    at.text_input(key="target_pair_search").set_value("CD3 BCMA").run()
    assert at.selectbox(key="target_pair_selection").options == ["BCMA/CD3", "BCMA/CD3/CD28"]
    assert at.selectbox(key="target_pair_selection").value is None
    at.selectbox(key="target_pair_selection").select("BCMA/CD3").run()
    assert not _generate(at).disabled
    at.text_input(key="target_pair_search").set_value("EGFR").run()
    assert at.selectbox(key="target_pair_selection").value is None
    assert _generate(at).disabled
    at.text_input(key="target_pair_search").set_value("nonexistent").run()
    assert _generate(at).disabled
    assert any("No matching combinations" in i.value for i in at.info)


def test_ui_load_failure_and_refresh_clear_selection():
    at = _pair_ui()
    at.selectbox(key="target_pair_selection").select("BCMA/CD3").run()
    next(b for b in at.button if b.label == "Refresh combinations").click().run()
    assert at.selectbox(key="target_pair_selection").value is None
    at.session_state["fail_load"] = True
    at.run()
    assert _generate(at).disabled
    assert any("could not be loaded" in e.value for e in at.error)
